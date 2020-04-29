from flask import Blueprint, request, redirect, jsonify
from common.libs.Helper import ops_render, iPagination, getCurrentDate
from common.libs.UrlManager import UrlManager
from common.models.member.Member import Member
from application import app,db


route_member = Blueprint('member_page', __name__)


@route_member.route('/comment')
def comment():
    return ops_render('member/comment.html')


@route_member.route('/index')
def index():
    resp_data = {}
    req = request.values
    resp = {'code':200, 'msg':'操作成功', 'data':{}}
    query = Member.query
    # 搜索
    status = int(req['status']) if 'status' in req and req['status'].isdigit() else ''
    if status and status in (0, 1):
        query = query.filter_by(status=status)

    mix_kw = req['mix_kw'] if 'mix_kw' in req else ''
    if mix_kw:
        query = query.filter(Member.nickname.ilike("%{}%".format(mix_kw)))

    # 分页
    page = int(req['p']) if 'p' in req and req['p'].isdigit() else 1
    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page':page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace('&p={}'.format(page), '')
    }

    pages = iPagination(page_params)
    offset = (page - 1) * app.config['PAGE_SIZE']
    list = query.order_by(Member.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()

    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['search'] = req
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    resp_data['current'] = 'index'
    return ops_render('member/index.html', resp_data)


@route_member.route('/info')
def info():
    resp_data = {}
    resp = {'code':200, 'msg':'操作成功','data':{}}
    req = request.args
    id = int(req['id']) if 'id' in req and req['id'].isdigit() else 0
    reback_url = UrlManager.buildUrl('/member/index')
    # 分开两步判断是因为查看个人详情需要ID，而如果没有ID就没必要进行数据库的查询了，直接重定向到member首页
    if id < 1:
        return redirect(reback_url)
    member_info = Member.query.filter_by(id=id).first()
    if not member_info:
        return redirect(reback_url)

    resp_data['member_info'] = member_info
    resp_data['current'] = 'index'
    return ops_render('member/info.html', resp_data)


@route_member.route('/set', methods=['POST', 'GET'])
def set():
    if request.method == 'GET':
        resp_data = {}
        req = request.args
        id = req.get('id', '')
        id = int(id) if id.isdigit() else 0
        reback_url = UrlManager.buildUrl('/member/index')
        if id < 1:
            return redirect(reback_url)

        member_info = Member.query.filter_by(id=id).first()
        if not member_info:
            return redirect(reback_url)

        if member_info.status != 1:
            return redirect(reback_url)

        resp_data['member_info'] = member_info
        resp_data['current'] = 'index'
        return ops_render('member/set.html', resp_data)

    resp = {'code':200, 'msg':'操作成功','data':{}}
    req = request.values
    id = int(req['id']) if 'id' in req and req['id'].isdigit() else 0
    nickname = req['nickname'] if 'nickname' in req else ''

    if not nickname or len(nickname) < 2:
        resp['code'] = -1
        resp['msg'] = '请输入正确的用户名'
        json = jsonify(resp)
        return jsonify(resp)

    if not id:
        resp['code'] = -1
        resp['msg'] = "参数有误"
        return jsonify(resp)

    member_info = Member.query.filter_by(id=id).first()
    if not member_info:
        resp['code'] = -1
        resp['data'] = '指定用户不存在'
        return jsonify(resp)

    member_info.nickname = nickname
    member_info.updated_time = getCurrentDate()
    db.session.add(member_info)
    db.session.commit()

    return jsonify(resp)



@route_member.route('/ops', methods=['POST', 'GET'])
def ops():
    resp = {'code':200, 'msg':'操作成功','data':{}}
    req = request.values
    id = int(req['id']) if 'id' in req and req['id'].isdigist()  else 0
    act = req['act'] if 'act' in req else ''

    if not id:
        resp['code'] = -1
        resp['msg'] = "请选择要操作的帐户"
        return jsonify(resp)

    if act not in ['remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试!"
        return jsonify(resp)

    member_info = Member.query.filter_by(id=id).first()
    if not member_info:
        resp['code'] = -1
        resp['data'] = '指定用户不存在'
        return jsonify(resp)

    if 'remove' == act:
        member_info.status = 0
    elif 'recover' == act:
        member_info.status = 1

    member_info.updated_time = getCurrentDate()
    db.session.add(member_info)
    db.session.commit()

    return jsonify(resp)