from flask import request, jsonify, g
from sqlalchemy import or_

from common.libs.UrlManager import UrlManager
from common.models.food.Food import Food
from common.models.food.FoodCat import FoodCat
from common.models.member.MemberCart import MemberCart
from web.controllers.api import route_api


@route_api.route('/food/index')
def foodIndex():
    resp = {'code':200, 'msg':'操作成功', 'data':{}}
    cat_list = FoodCat.query.filter_by(status=1).order_by(FoodCat.weight.desc()).limit(3).all()
    data_cat_list = []
    data_cat_list.append({
        'id':0,
        'name':'全部'
    })
    if cat_list:
        for item in cat_list:
            tmp_data = {
                'id': item.id,
                'name': item.name
            }
            data_cat_list.append(tmp_data)
    resp['data']['cat_list'] = data_cat_list

    food_list = Food.query.filter_by(status=1).order_by(Food.total_count.desc(),Food.cat_id.desc()).limit(4).all()
    data_food_list = []
    if food_list:
        for item in food_list:
            tmp_data = {
                'id': item.id,
                'pic_url': UrlManager.buildImageUrl(item.main_image)
            }
            data_food_list.append(tmp_data)
    resp['data']['banner_list'] = data_food_list
    return jsonify(resp)


@route_api.route('/food/search')
def foodSearch():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    query = Food.query

    cat_id = int(req['cat_id']) if 'cat_id' in req and req['cat_id'].isdigit() else -1
    page = int(req['p']) if 'p' in req and req['p'].isdigit() else 1
    page_size = 4
    offset = (page - 1) * page_size

    if cat_id > 0:
        query = query.filter(Food.cat_id==cat_id)

    if 'mix_kw' in req:
        rule = or_(Food.name.ilike('%{}%'.format(req['mix_kw'])),
                   Food.tags.ilike('%{}%'.format(req['mix_kw'])))
        query = query.filter(rule)

    list = query.filter(Food.status == 1).order_by(Food.total_count.desc(), Food.id.desc())\
        .offset(offset).limit(page_size).all()
    data_food_list = []
    if list:
        for item in list:
            tmp_data = {
                'id': item.id,
                'name': item.name,
                'price': str(item.price),
                'min_price': str(item.price),
                'pic_url':UrlManager.buildImageUrl(item.main_image),
            }
            data_food_list.append(tmp_data)

    resp['data']['list'] = data_food_list
    resp['data']['has_more'] = 0 if len(data_food_list) < page_size else 1
    return jsonify(resp)


@route_api.route('food/info')
def foodInfo():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    id = int(req['id']) if 'id' in req and req['id'].isdigit() else 0
    food_info = Food.query.filter_by(id=id).first()
    if not food_info:
        resp['code'] = -1
        resp['msg'] = '美食信息不存在'
        return jsonify(resp)
    if food_info.status != 1:
        resp['code'] = -1
        resp['msg'] = '该美食信息已被禁用'
        return jsonify(resp)

    member_info = g.member_info
    cart_number = 0
    if member_info:
        cart_number = MemberCart.query.filter_by(member_id=member_info.id).count()

    resp['data']['info'] = {
        'id': food_info.id,
        'name': food_info.name,
        'summary': food_info.summary,
        'total_count': food_info.total_count,
        'comment_count': food_info.comment_count,
        'stock': food_info.stock,
        'price': str(food_info.price),
        'main_image': UrlManager.buildImageUrl(food_info.main_image),
        'pics':[UrlManager.buildImageUrl(food_info.main_image)]
    }
    resp['data']['cart_number'] = cart_number
    return jsonify(resp)














