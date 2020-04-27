from flask import Blueprint, request, redirect, jsonify
from sqlalchemy import or_

from application import app, db
from common.libs.Helper import getCurrentDate
from common.libs.Helper import ops_render, iPagination
from common.libs.UrlManager import UrlManager
from common.libs.user.UserService import UserService
from common.models.AppAccessLog import AppAccessLog
from common.models.User import User

route_account = Blueprint('account_page', __name__)


@route_account.route('/index')
def index():
    resp_data = {}
    query = User.query
    req = request.values

    if 'mix_kw' in req:
        rule = or_(User.nickname.ilike("%{}%".format(req['mix_kw'])),
                   User.mobile.ilike("%{}%".format(req['mix_kw'])))
        query = query.filter(rule)

    if 'status' in req and req['status'].isdigit():
        if int(req['status']) in (0, 1):
            query = query.filter(User.status == int(req['status']))

    # 确保有page参数并且是整数
    page = int(req['p']) if ('p' in req and req['p'].isdigit()) else 1
    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), ''),

    }
    # app.logger.info(page)
    # app.logger.info(request.full_path, request.path)
    pages = iPagination(page_params)
    # 偏移量
    offset = (page - 1) * app.config['PAGE_SIZE']
    limit = app.config['PAGE_SIZE'] * page

    list = query.order_by(User.uid.desc()).all()[offset:limit]
    resp_data['pages'] = pages
    resp_data['list'] = list
    resp_data['search_con'] = req
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    return ops_render('account/index.html', resp_data)


@route_account.route('/info')
def info():
    resp_data = {}
    req = request.args  # 获取get的参数
    uid = (req.get('id', ''))
    # 确保id的参数是整数
    uid = int(uid) if uid.isdigit() else 0
    reback_url = UrlManager.buildUrl('/account/index')
    if uid < 1:
        return redirect(reback_url)
    user_info = User.query.filter_by(uid=uid).first()
    if not user_info:
        return redirect(reback_url)

    query = AppAccessLog.query
    query = query.filter_by(uid=uid)

    page = int(req['p']) if ('p' in req and req['p'].isdigit()) else 1
    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), '')

    }
    pages = iPagination(page_params)
    offset = (page - 1) * app.config['PAGE_SIZE']
    limit = app.config['PAGE_SIZE'] * page

    list = query.order_by(AppAccessLog.created_time.desc())[offset: limit]
    resp_data['pages'] = pages
    resp_data['user_info'] = user_info
    resp_data['list'] = list
    return ops_render('account/info.html', resp_data)


@route_account.route('/set', methods=['POST', 'GET'])
def set():
    default_pwd = '******'
    if request.method == 'GET':
        resp_data = {}
        req = request.args
        uid = req.get('id', '')
        uid = int(uid) if uid.isdigit() else 0
        user_info = None
        if uid:
            user_info = User.query.filter_by(uid=uid).first()
        resp_data['user_info'] = user_info
        return ops_render('account/set.html', resp_data)

    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values

    id = req['id'] if 'id' in req else 0
    nickname = req['nickname'] if 'nickname' in req else ''
    mobile = req['mobile'] if 'mobile' in req else ''
    email = req['email'] if 'email' in req else ''
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

    if not nickname or len(nickname) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入正确的用户名'
        return jsonify(resp)

    if not mobile or len(mobile) < 11:
        resp['code'] = -1
        resp['msg'] = '请输入正确的手机号'
        return jsonify(resp)

    if not email or len(email) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入正确的邮箱'
        return jsonify(resp)

    if not login_name or len(login_name) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入正确的登录用户名'
        return jsonify(resp)

    if not login_pwd or len(login_pwd) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入正确的登录密码'
        return jsonify(resp)

    has_login_name = User.query.filter(User.login_name == login_name, User.uid != id).first()
    if has_login_name:
        resp['code'] = -1
        resp['msg'] = '登录用户名已存在,请重新输入'
        return jsonify(resp)

    user_info = User.query.filter_by(uid=id).first()
    if user_info:
        user_model = user_info
    else:
        user_model = User()
        user_model.created_time = getCurrentDate()
        user_model.login_salt = UserService.geneSalt()

    user_model.nickname = nickname
    user_model.mobile = mobile
    user_model.email = email
    user_model.login_name = login_name
    if login_pwd != default_pwd:
        user_model.login_pwd = UserService.genePwd(login_pwd, user_model.login_salt)
    user_model.updated_time = getCurrentDate()

    db.session.add(user_model)
    db.session.commit()

    return jsonify(resp)


@route_account.route('/ops', methods=['POST'])
def ops():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''
    # app.logger.info(type(id))
    if not id:
        resp['code'] = -1
        resp['msg'] = "请选择要操作的帐户"
        return jsonify(resp)

    if act not in ['remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试!"
        return jsonify(resp)

    user_info = User.query.filter_by(uid=id).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "指定帐户不存在"
        return jsonify(resp)

    if act == 'remove':
        user_info.status = 0
    elif act == 'recover':
        user_info.status = 1

    user_info.updated_time = getCurrentDate()

    db.session.add(user_info)
    db.session.commit()

    return jsonify(resp)
