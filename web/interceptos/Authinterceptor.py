import re

from flask import request, redirect, g

from application import app
from common.libs.LogService import LogService
from common.libs.UrlManager import UrlManager
from common.libs.user.UserService import UserService
from common.models.User import User


@app.before_request
def before_request():
    """
    用户未登录的话重定向至登录页面，避免循环重定向至登录页面，用路径来判断;
    静态文件不需要检测是否登录，直接返回；再判断页面是否是login，
    好像无法解决用户再已登录的情况下在访问login界面,不会自动重定向(在用户已经登录的时候，访问登陆界面，)
    :return:
    """
    path = request.path
    ignore_urls = app.config["IGNORE_URLS"]
    ignore_check_login_urls = app.config["IGNORE_CHECK_LOGIN_URLS"]
    # 静态文件不需要检测是否已经登录
    pattern = re.compile("%s" % "|".join(ignore_check_login_urls))
    if pattern.match(path):
        return

    user_info = check_login()
    # app.logger.info(user_info)
    g.current_user = None
    if user_info:
        g.current_user = user_info

    # 加入日志
    LogService.addAceesLog()

    pattern = re.compile("%s" % "|".join(ignore_urls))
    if pattern.match(path):
        if not user_info:
            return
        else:
            return redirect(UrlManager.buildUrl('/'))

    if not user_info:
        return redirect(UrlManager.buildUrl('/user/login'))


def check_login():
    """
    判断用户是否已登录
    从request取出cookies,再取出有关登录认证的cookie，以#分割后的auth_info判断长度是否为2，
    再然后用auth_info[1]即uid来向数据库的用户表查询是否有该用户，判断有无，
    再用auth_info[0]即auth_code与user_info[1]即uid生成的auth_code判断是否相等
    :return:
    """
    cookies = request.cookies
    auth_cookie = cookies[app.config['AUTH_COOKIE_NAME']] if app.config['AUTH_COOKIE_NAME'] in cookies else None

    if auth_cookie is None:
        return False

    auth_info = auth_cookie.split('#')

    if len(auth_info) != 2:
        return False
    try:
        user_info = User.query.filter_by(uid=auth_info[1]).first()
    except Exception:
        return False

    if user_info is None:
        return False

    if auth_info[0] != UserService.geneAuthCode(user_info):
        return False

    # 判断用户是否被禁用
    if user_info.status != 1:
        return False

    return user_info
