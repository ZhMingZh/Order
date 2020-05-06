from web.controllers.api import route_api
from flask import request, jsonify, g
from common.models.food.Food import Food
from common.libs.member.CartService import CartService


@route_api.route('/cart/set', methods=['POST'])
def setCart():
    resp = {'code':200, 'msg':'添加成功', 'data':{}}
    req = request.values
    food_id = int(req['id']) if 'id' in req and req['id'].isdigit() else 0
    number = int(req['number']) if 'number' in req and req['number'].isdigit() else 0
    if food_id < 0 or number < 1:
        resp['code'] = -1
        resp['msg'] = '添加购物车失败 -1'
        return jsonify(resp)

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '添加购物车失败 -2'
        return jsonify(resp)

    food_info = Food.query.filter_by(id=food_id).first()
    if not food_info:
        resp['code'] = -1
        resp['msg'] = '添加购物车失败 -3'
        return jsonify(resp)

    if food_info.stock < number:
        resp['code'] = -1
        resp['msg'] = '添加购物车失败,库存不足'
        return jsonify(resp)

    ret = CartService.setItems(member_info.id,food_id,number)
    if not ret:
        resp['code'] = -1
        resp['msg'] = '添加购物车失败 -4'
        return jsonify(resp)

    # resp['data'][]
    return jsonify(resp)
