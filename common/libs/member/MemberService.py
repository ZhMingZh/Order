import hashlib
import json
import random
import string

import requests

from application import app


class MemberService(object):

    @staticmethod
    def geneAuthCode(member_info):
        m = hashlib.md5()
        string = "%s-%s-%s" % (
            member_info.id, member_info.salt, member_info.status)
        m.update(string.encode('utf-8'))
        return m.hexdigest()

    @staticmethod
    def geneSalt(length=16):
        keys_list = [random.choice(string.ascii_letters + string.digits) for i in range(length)]
        return ''.join(keys_list)

    @staticmethod
    def getWeChatOpenId(code):
        url = 'https://api.weixin.qq.com/sns/jscode2session?' \
              'appid={0}&secret={1}&js_code={2}&grant_type=authorization_code'. \
            format(app.config['APPID'], app.config['APP_SECRET'], code)
        r = requests.get(url)
        res = json.loads(r.text)
        openid = None
        if 'openid' in res:
            openid = res['openid']
        return openid
