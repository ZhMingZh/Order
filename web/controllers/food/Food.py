from flask import Blueprint, request, jsonify, redirect
from common.libs.Helper import ops_render
from common.models.food.FoodCat import FoodCat
from common.models.food.Food import Food
from common.models.food.FoodStockChangeLog import FoodStockChangeLog
from common.libs.Helper import getCurrentDate, getDictFilterFiled, iPagination
from application import app, db
from decimal import Decimal
from common.libs.UrlManager import UrlManager
from sqlalchemy import or_

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
    req = request.values
    query = Food.query

    status = int(req['status']) if 'status' in req and req['status'].isdigit() else -1
    cat_id = int(req['cat_id']) if 'cat_id' in req and req['cat_id'].isdigit() else -1
    page = int(req['p']) if 'p' in req and req['p'].isdigit() else 1
    # 搜索的关键词
    if 'mix_kw' in req:
        rule = or_(Food.name.ilike('%{}%'.format(req['mix_kw'])),
                   Food.tags.ilike('%{}%'.format(req['mix_kw'])))
        query = query.filter(rule)

    if status > -1:
        query = query.filter(Food.status==status)

    if cat_id > 0:
        query = query.filter(Food.cat_id==cat_id)

    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace('&p={}'.format(page), ''),
    }

    pages = iPagination(page_params)
    offset = (page - 1) * app.config['PAGE_SIZE']

    cat_mapping = getDictFilterFiled(FoodCat, 'id', 'id', [])
    food_info = query.order_by(Food.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()

    resp_data['pages'] = pages
    resp_data['food_info'] = food_info
    resp_data['current'] = 'index'
    resp_data['cat_mapping'] = cat_mapping
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    resp_data['search_con'] = req
    return ops_render('food/index.html', resp_data)


@route_food.route('/set', methods=['POST', 'GET'])
def set():
    if request.method == 'GET':
        resp_data = {}
        req = request.args
        ids = req.get('id', '')
        id = int(ids) if ids.isdigit() else 0
        food_info = Food.query.filter_by(id=id).first()
        if food_info and food_info.status != 1:
            return redirect(UrlManager.buildUrl('/food/index'))

        cat_list = FoodCat.query.all()
        resp_data['current'] = 'index'
        resp_data['cat_list'] = cat_list
        resp_data['food_info'] = food_info
        return ops_render('food/set.html', resp_data)

    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    id = int(req['id']) if 'id' in req and req['id'].isdigit() else 0
    cat_id = int(req['cat_id']) if 'cat_id' in req and req['cat_id'].isdigit() else 0
    name = req['name'] if 'name' in req else ''
    price = req['price'] if 'price' in req else  0
    main_image = req['main_image'] if 'main_image' in req else ''
    summary = req['summary'] if 'summary' in req else ''
    stock = int(req['stock']) if 'stock' in req and req['stock'].isdigit() else 0
    tags = req['tags'] if 'tags' in req else ''

    price = Decimal(price).quantize(Decimal('0.00'))

    if cat_id < 1:
        resp['code'] = -1
        resp['msg'] = '请选择分类'
        return jsonify(resp)

    if not name or len(name) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的名字'
        return jsonify(resp)

    if price <= 0:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的售卖价格'
        return jsonify(resp)

    if not main_image or len(main_image) < 3:
        resp['code'] = -1
        resp['msg'] = '请上传封面图'
        return jsonify(resp)

    if not summary or len(summary) < 10:
        resp['code'] = -1
        resp['msg'] = '请输入描述，并且不能少于10个字符'
        return jsonify(resp)

    if stock < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的库存量'
        return jsonify(resp)

    if not tags or len(tags) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入标签，便于搜索'
        return jsonify(resp)

    # has_food_name = Food.query.filter(Food.name==name).first()
    # if has_food_name:
    #     resp['code'] = -1
    #     resp['msg'] = '菜名已存在，请重新输入'
    #     return jsonify(resp)

    food_info = Food.query.filter_by(id=id).first()
    before_stock = 0

    if food_info:
        model_food = food_info
        before_stock = model_food.stock
    else:
        model_food = Food()
        model_food.created_time = getCurrentDate()

    model_food.cat_id = cat_id
    model_food.name = name
    model_food.main_image = main_image
    model_food.stock = stock
    model_food.price = price
    model_food.summary = summary
    model_food.tags = tags
    model_food.updated_time = getCurrentDate()

    db.session.add(model_food)
    db.session.commit()

    model_stock_change = FoodStockChangeLog()
    model_stock_change.food_id = model_food.id
    model_stock_change.unit = model_food.stock - before_stock
    model_stock_change.total_stock = stock
    model_stock_change.note = ''
    model_stock_change.created_time = getCurrentDate()

    db.session.add(model_stock_change)
    db.session.commit()

    return jsonify(resp)



@route_food.route('/info')
def info():
    resp_data = {}
    req = request.values
    id = int(req['id']) if 'id' in req and req['id'].isdigit() else 0
    reback_url = UrlManager.buildUrl('/food/index')
    if not id:
        return redirect(reback_url)
    food_info = Food.query.filter_by(id=id).first()
    if not food_info:
        return redirect(reback_url)

    stock_change_list = FoodStockChangeLog.query.filter(FoodStockChangeLog.food_id==id)\
            .order_by(FoodStockChangeLog.id.desc()).all()

    resp_data['stock_change_list'] = stock_change_list
    resp_data['food_info'] = food_info
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


@route_food.route('/food_ops', methods=['POST'])
def food_ops():
    resp = {'code':200, 'msg': '操作成功', 'data':{}}
    req = request.values

    id = int(req['id']) if 'id' in req and req['id'].isdigit() else 0
    act = req['act'] if 'act' in req else ''

    food_info = Food.query.filter_by(id=id).first()

    if not food_info:
        resp['code'] = -1
        resp['msg'] = '无此菜'
        return jsonify(resp)

    if act == 'remove':
        food_info.status = 0
    elif act == 'recover':
        food_info.status = 1

    food_info.update_time = getCurrentDate()
    db.session.add(food_info)
    db.session.commit()

    return jsonify(resp)


