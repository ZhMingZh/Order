SERVER_PORT = 8999
SQLALCHEMY_ECHO = False
DEBUG = False
AUTH_COOKIE_NAME = 'mooc_food'

# 过滤url
IGNORE_URLS = [
    "^/user/login",
    "^/api"
]

IGNORE_CHECK_LOGIN_URLS = [
    "^/static",
    "^favicon.ico"
]

# 分页参数
PAGE_SIZE = 10
PAGE_DISPLAY = 10

STATUS_MAPPING = {
    "1": "正常",
    "0": "已删除"
}

# 小程序相关
APPID = 'wx8f8d1afbabf8223d'
APP_SECRET = '14d59906fcfe9d09f53e7044b9895a6a'
