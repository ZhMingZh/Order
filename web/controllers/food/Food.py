from flask import Blueprint, request, jsonify
from common.libs.Helper import ops_render
from common.models.food.FoodCat import FoodCat
from common.libs.Helper import getCurrentDate
from application import app, db
route_food = Blueprint('food_page', __name__)


@route_food.route('/cat')
def cat():
    resp_data = {}
    req = request.values
    query = FoodCat.query

    if 'status' in req and req['status'].isdigit():
        if int(req['status']) in (0,1):
            query = query.filter(FoodCat.status==int(req['status']))

    food_cat_info = query.order_by(FoodCat.id.desc()).all()
    resp_data['food_cat_info'] = food_cat_info
    resp_data['current'] = 'cat'
    resp_data['search_con'] = req
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    return ops_render('food/cat.html', resp_data)


@route_food.route('/index')
def index():
    resp_data = {}
    resp_data['current'] = 'index'
    return ops_render('food/index.html', resp_data)


@route_food.route('/set')
def set():
    resp_data = {}
    resp_data['current'] = 'index'
    return ops_render('food/set.html', resp_data)


@route_food.route('/info')
def info():
    resp_data = {}
    resp_data['current'] = 'index'
    return ops_render('food/info.html', resp_data)


@route_food.route('/cat_set', methods=["POST", 'GET'])
def cat_set():
    if request.method == 'GET':
        resp_data = {}
        req = request.args
        id = req.get('id', '')
        id = int(id) if id.isdigit() else 0
        cat_info = None
        if id:
            cat_info = FoodCat.query.filter_by(id=id).first()
        resp_data['cat_info'] = cat_info
        resp_data['current'] = 'cat'
        return ops_render('food/cat_set.html', resp_data)

    resp = {'code':200, 'msg':'操作成功', 'data':{}}
    req = request.values

    id = int(req['id']) if 'id' in req and req['id'].isdigit() else 0
    name = req['name'] if 'name' in req else ''
    weight = int(req['weight']) if 'weight' in req and req['weight'].isdigit() else 1

    if not name and len(name) < 2:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的用户名'
        return jsonify(resp)

    if weight < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的权重，大于等于1'
        return jsonify(resp)
    #是否存在分类名
    has_name = FoodCat.query.filter(FoodCat.name==name, FoodCat.id != id).first()
    if has_name:
        resp['code'] = -1
        resp['msg'] = '菜品类已存在,请重新输入'
        return jsonify(resp)

    food_cat_info = FoodCat.query.filter_by(id=id).first()

    if food_cat_info:
        model_food_cat = food_cat_info
    else:
        model_food_cat = FoodCat()
        model_food_cat.created_time = getCurrentDate()

    model_food_cat.name = name
    model_food_cat.weight = weight
    model_food_cat.status = 1
    model_food_cat.updated_time = getCurrentDate()

    db.session.add(model_food_cat)
    db.session.commit()

    return jsonify(resp)


@route_food.route('/ops', methods=['POST'])
def ops():
    resp = {'code':200, 'msg': '操作成功', 'data':{}}
    req = request.values

    id = int(req['id']) if 'id' in req and req['id'].isdigit() else 0
    act = req['act'] if 'act' in req else ''

    if id < 1:
        resp['code'] = -1
        resp['msg'] = '参数有误'
        return jsonify(resp)

    if not act or act not in ('remove', 'recover'):
        resp['code'] = -1
        resp['msg'] = '操作有勿'
        return jsonify(resp)

    food_cat_info = FoodCat.query.filter_by(id=id).first()

    if not food_cat_info:
        resp['code'] = -1
        resp['msg'] = '无此用户'
        return jsonify(resp)

    if act == 'remove':
        food_cat_info.status = 0
    elif act == 'recover':
        food_cat_info.status = 1

    food_cat_info.update_time = getCurrentDate()
    db.session.add(food_cat_info)
    db.session.commit()

    return jsonify(resp)


