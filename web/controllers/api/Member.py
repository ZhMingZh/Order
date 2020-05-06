from flask import request, jsonify, g

from application import db
from common.libs.Helper import getCurrentDate
from common.libs.member.MemberService import MemberService
from common.models.member.Member import Member
from common.models.member.OauthMemberBind import OauthMemberBind
from web.controllers.api import route_api
from common.models.food.WxShareHistory import WxShareHistory
# route_api = Blueprint('api_page', __name__)


@route_api.route('/member/login', methods=['POST', 'GET'])
def login():
    resp = {'code':200, 'msg': '操作成功', 'data':{}}
    req = request.values
    code = req['code'] if 'code' in req else ''
    if not code:
        resp['code'] = -1
        resp['msg'] = '需要code'
        return jsonify(resp)
    # 通过前端传回来的code，再通过链接获取openid

    openid = MemberService.getWeChatOpenId(code)

    if openid is None:
        resp['code'] = -1
        resp['msg'] = '调用微信出错'
        return jsonify(resp)

    nickname = req['nickName'] if 'nickName' in req else ''
    sex = req['gender'] if 'gender' in req else ''
    avatar = req['avatarUrl'] if 'avatarUrl' in req else ''

    # 判断是否已经绑定了openid，注册了直接返回一些信息
    oauth_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first()
    if not oauth_info:
        # 会员信息
        model_member = Member()
        model_member.nickname = nickname
        model_member.sex = sex
        model_member.avatar = avatar
        model_member.salt = MemberService.geneSalt()
        model_member.reg_ip = request.remote_addr
        model_member.updated_time = model_member.created_time = getCurrentDate()
        db.session.add(model_member)
        db.session.commit()

        # 授权信息
        model_oauth = OauthMemberBind()
        model_oauth.member_id = model_member.id
        model_oauth.type = 1
        model_oauth.extra = ''
        model_oauth.openid = openid
        model_oauth.updated_time = model_oauth.created_time = getCurrentDate()
        db.session.add(model_oauth)
        db.session.commit()
    #
        oauth_info = model_oauth

    member_info = Member.query.filter_by(id=oauth_info.member_id).first()
    token = "%s#%s" % (MemberService.geneAuthCode(member_info), member_info.id)
    resp['data'] = {'token': token}
    return jsonify(resp)


@route_api.route("/member/check_reg",methods = [ "GET","POST" ])
def checkReg():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    code = req['code'] if 'code' in req else ''
    if not code or len(code) < 1:
        resp['code'] = -1
        resp['msg'] = "需要code"
        return jsonify(resp)

    openid = MemberService.getWeChatOpenId(code)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = "调用微信出错"
        return jsonify(resp)

    oauth_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first()
    if not oauth_info:
        resp['code'] = -1
        resp['msg'] = "未绑定"
        return jsonify(resp)

    member_info = Member.query.filter_by( id = oauth_info.member_id).first()
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "未查询到绑定信息"
        return jsonify(resp)

    token = "%s#%s"%( MemberService.geneAuthCode( member_info ),member_info.id )
    resp['data'] = { 'token':token }
    return jsonify(resp)


@route_api.route('/member/share', methods=['POST'])
def memberShare():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    url = req['url'] if 'url' in req else ''
    member_info = g.member_info
    model_share = WxShareHistory()
    if member_info:
        model_share.member_id = member_info.id
    model_share.share_url = url
    model_share.created_time = getCurrentDate()
    db.session.add(model_share)
    db.session.commit()
    return jsonify(resp)