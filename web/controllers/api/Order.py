from web.controllers.api import route_api
from flask import request, jsonify, g
from common.models.food.Food import Food
from common.libs.UrlManager import UrlManager
from common.libs.pay.PayService import PayService
import json, decimal
from common.libs.member.CartService import CartService

@route_api.route('/order/info', methods=['POST', 'GET'])
def orderInfo():
    resp = {'code':200, 'msg':'操作成功', 'data':{}}
    req = request.values
    params_goods = req['goods'] if 'goods' in req else None
    params_goods_list = []
    if params_goods:
        params_goods_list = json.loads(params_goods)

    number_dic = {}
    for item in params_goods_list:
        number_dic[item['id']] = item['number']

    food_ids = number_dic.keys()
    food_list = Food.query.filter(Food.id.in_(food_ids)).all()
    data_food_list = []
    yun_price = pay_price = decimal.Decimal(0.00)
    if food_list:
        for item in food_list:
            tmp_data = {
                'id': item.id,
                'name': item.name,
                'price': str(item.price),
                'pic_url': UrlManager.buildImageUrl(item.main_image),
                'number':number_dic[item.id],
            }
            pay_price += item.price * int(number_dic[item.id])
            data_food_list.append(tmp_data)

    default_address = {
        'name': "编程浪子",
        'mobile': "12345678901",
        'detail': "上海市浦东新区XX",
    }

    resp['data']['food_list'] = data_food_list
    resp['data']['pay_price'] = str(pay_price)
    resp['data']['yun_price'] = str(yun_price)
    resp['data']['total_price'] = str(pay_price + yun_price)
    resp['data']['default_address'] = default_address

    return jsonify(resp)


@route_api.route('/order/create', methods=['POST'])
def orderCreate():
    resp = {'code':200, 'msg':'操作成功', 'data':{}}
    req = request.values
    type = req['type'] if 'type' in req else ''
    goods = req['goods'] if 'goods' in req else None
    items = []
    if goods:
        items = json.loads(goods)

    if len(items) < 1:
        resp['code'] = -1
        resp['msg'] = '下单失败: 没有选择商品'
        return jsonify(resp)

    member_info = g.member_info
    target = PayService()
    params = {}
    resp = target.createOrder(member_info.id, items, params)

    if resp['code'] == 200 and type == 'cart':
        CartService.delItems(member_info.id, items)

    return jsonify(resp)