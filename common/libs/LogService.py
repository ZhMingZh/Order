import json
import re

from flask import request, g

from application import db
from common.libs.Helper import getCurrentDate
from common.models.AppAccessLog import AppAccessLog
from common.models.AppErrorLog import AppErrorLog


class LogService(object):

    @staticmethod
    def addAceesLog():
        target = AppAccessLog()
        if g.current_user:
            target.uid = g.current_user.uid
        target.referer_url = request.referrer
        path = request.path
        if re.match(r'^/account/info', path):
            return True
        target.target_url = request.url
        target.query_params = json.dumps(request.values.to_dict())
        target.ua = request.headers.get('User-Agent')
        target.ip = request.remote_addr
        target.created_time = getCurrentDate()

        db.session.add(target)
        db.session.commit()
        return True

    @staticmethod
    def addErrorLog(content):
        if 'favicon.ico' in request.url:
            return
        target = AppErrorLog()
        target.referer_url = request.referrer
        target.target_url = request.url
        target.query_params = json.dumps(request.values.to_dict())
        target.content = content
        target.created_time = getCurrentDate()
        db.session.add(target)
        db.session.commit()
        return True
