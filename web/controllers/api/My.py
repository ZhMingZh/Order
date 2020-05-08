from web.controllers.api import route_api
from flask import request, jsonify, g
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.pay.PayOrder import PayOrder
from common.models.food.Food import Food
from common.libs.Helper import getDictFilterFiled, selectFilterObj
from common.libs.UrlManager import UrlManager


@route_api.route('/my/order')
def myOrderList():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req  = request.values
    member_info = g.member_info
    status = int(req['status']) if 'status' in req else 0
    query = PayOrder.query.filter_by(member_id=member_info.id)
    '''"-8","-7","-6","-5","1","0" '''
    if status == -8:  #未付款
        query = query.filter(PayOrder.status == -8)
    elif status == -7: #待发货
        query = query.filter(
            PayOrder.status == 1, PayOrder.express_status == -7, PayOrder.comment_status == 0)
    elif status == -6: #待收货
        query = query.filter(
            PayOrder.status == 1, PayOrder.express_status == -6, PayOrder.comment_status == 0)
    elif status == -5: #待评价
        query = query.filter(
            PayOrder.status == 1, PayOrder.express_status == 1, PayOrder.comment_status == 0)
    elif status == 1: #已完成
        query = query.filter(
            PayOrder.status == 1, PayOrder.express_status == 1, PayOrder.comment_status == 1)
    elif status == 0: #已关闭
        query = query.filter(PayOrder.status == 0)
    else:
        resp['code'] = -1
        resp['msg'] = '错误的状态'
        return jsonify(resp)

    pay_order_list =  query.order_by(PayOrder.id.desc()).all()
    data_pay_order_list = []
    if pay_order_list:
        # 从订单表中取出所有对应的id, [17, 18, 19]
        pay_order_ids = selectFilterObj(pay_order_list, 'id')
        # 再从获得的订单id列表过滤出所有符合的pay_order_item
        pay_order_item_list = PayOrderItem.query.filter(PayOrderItem.pay_order_id.in_(pay_order_ids)).all()
        food_ids = selectFilterObj(pay_order_item_list, 'food_id')
        food_dic = getDictFilterFiled(Food, Food.id, 'id', food_ids)
        # 订单号id为key, value为商品信息
        pay_order_item_dic = {}
        if pay_order_item_list:
            for item in pay_order_item_list:
                if item.pay_order_id not in pay_order_item_dic:
                    pay_order_item_dic[item.pay_order_id] = []
                #
                tmp_food_info = food_dic[item.food_id]
                pay_order_item_dic[item.pay_order_id].append({
                    'id': item.id,
                    'food_id': item.food_id,
                    'quantity': item.quantity,
                    'pic_url': UrlManager.buildImageUrl(tmp_food_info.main_image),
                    'name': tmp_food_info.name

                })

        for item in pay_order_list:
            tmp_data = {
                'status': item.pay_status,
                'status_desc': item.status_desc,
                'date': item.created_time.strftime('%Y-%m-%d %H:%M:%S'),
                'order_number': item.order_number,
                'note': item.note,
                'total_price': str(item.total_price),
                'goods_list': pay_order_item_dic[item.id]
            }
            data_pay_order_list.append(tmp_data)

    resp['data']['pay_order_list'] = data_pay_order_list
    return jsonify(resp)