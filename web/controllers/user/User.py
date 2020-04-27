import json

from flask import Blueprint, request, jsonify, make_response, redirect, g

from application import app, db
from common.libs.Helper import ops_render
from common.libs.UrlManager import UrlManager
from common.libs.user.UserService import UserService
from common.models.User import User

route_user = Blueprint('user_page', __name__)


@route_user.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return ops_render('user/login.html')
    resp = {'code': 200, 'msg': '登录成功', 'data': {}}
    req = request.values
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

    if not login_name or len(login_name) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入正确的用户名'
        return jsonify(resp)

    if not login_pwd or len(login_pwd) < 6:
        resp['code'] = -1
        resp['msg'] = '请输入正确的密码'
        return jsonify(resp)

    user_info = User.query.filter_by(login_name=login_name).first()

    if not user_info:
        resp['code'] = -1
        resp['msg'] = '请输入正确的用户名和密码-1'
        return jsonify(resp)

    if user_info.login_pwd != UserService.genePwd(login_pwd, user_info.login_salt):
        resp['code'] = -1
        resp['msg'] = '请输入正确的用户名和密码-2'
        return jsonify(resp)

    if user_info.status != 1:
        resp['code'] = -1
        resp['msg'] = '帐户已被禁用,请联系管理员处理.'
        return jsonify(resp)

    response = make_response(json.dumps(resp))
    response.set_cookie(app.config['AUTH_COOKIE_NAME'], "%s#%s" % (
        UserService.geneAuthCode(user_info), user_info.uid), 60 * 60 * 24 * 120)  # 120天有效期

    return response


@route_user.route('/edit', methods=["POST", "GET"])
def edit():
    if request.method == "GET":
        return ops_render('user/edit.html', {'current': 'edit'})
    resp = {'code': 200, 'msg': "操作成功", 'data': {}}
    res = request.values
    nickname = res['nickname'] if 'nickname' in res else ''
    email = res['email'] if 'email' in res else ''

    if not nickname or len(nickname) < 2:
        resp['code'] = -1
        resp['msg'] = "请输入正确的用户名"
        return jsonify(resp)

    if not email or len(email) < 2:
        resp['code'] = -1
        resp['msg'] = "请输入正确的邮箱"
        return jsonify(resp)

    user_info = g.current_user
    user_info.nickname = nickname
    user_info.email = email
    db.session.add(user_info)
    db.session.commit()

    return jsonify(resp)


@route_user.route('/reset_pwd', methods=["POST", "GET"])
def reset_pwd():
    if request.method == 'GET':
        return ops_render('user/reset_pwd.html', {'current': 'reset_pwd'})

    resp = {'code': 200, 'msg': "操作成功", 'data': {}}
    res = request.values
    old_password = res['old_password'] if 'old_password' in res else ''
    new_password = res['new_password'] if 'new_password' in res else ''

    if not old_password or len(old_password) < 6:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的原密码"
        return jsonify(resp)

    if not new_password or len(new_password) < 6:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的新密码"
        return jsonify(resp)

    if new_password == old_password:
        resp['code'] = -1
        resp['msg'] = "请重新输入新密码，新密码与原密码不能相同"
        return jsonify(resp)

    user_info = g.current_user
    if UserService.genePwd(old_password, user_info.login_salt) != user_info.login_pwd:
        resp['code'] = -1
        resp['msg'] = "原密码不正确，请重新输入"
        return jsonify(resp)

    user_info.login_pwd = UserService.genePwd(new_password, user_info.login_salt)

    db.session.add(user_info)
    db.session.commit()

    # 因为更改密码之后，cookie失效，可以在此步骤更新下cookies,这样就不会退出在登录了
    response = make_response(json.dumps(resp))
    response.set_cookie(app.config['AUTH_COOKIE_NAME'], '%s#%s' %
                        (UserService.geneAuthCode(user_info), user_info.uid), 120 * 24 * 60 * 60)

    return response


@route_user.route('/logout')
def logout():
    response = make_response(redirect(UrlManager.buildUrl('/user/login')))
    response.delete_cookie(app.config['AUTH_COOKIE_NAME'])
    return response
