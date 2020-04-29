from application import app

"""
拦截器相关
"""
from web.interceptos.Authinterceptor import *
from web.interceptos.Errorinterceptor import *


"""
蓝图相关,对所有的url进行蓝图功能配置
"""
from web.controllers.index import route_index
from web.controllers.user.User import route_user
from web.controllers.account.Account import route_account
from web.controllers.member.Member import route_member
from web.controllers.finance.Finance import route_finance
from web.controllers.stat.Stat import route_stat
from web.controllers.food.Food import route_food
from web.controllers.api import route_api

app.register_blueprint(route_api, url_prefix='/api')
app.register_blueprint(route_index, url_prefix='/')
app.register_blueprint(route_user, url_prefix='/user')
app.register_blueprint(route_account, url_prefix='/account')
app.register_blueprint(route_member, url_prefix='/member')
app.register_blueprint(route_finance, url_prefix='/finance')
app.register_blueprint(route_stat, url_prefix='/stat')
app.register_blueprint(route_food, url_prefix='/food')