# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, Numeric
from sqlalchemy.schema import FetchedValue
from application import db


class FoodSaleChangeLog(db.Model):
    __tablename__ = 'food_sale_change_log'

    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), info='商品id')
    quantity = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='售卖数量')
    price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='售卖金额')
    member_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='会员id')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='售卖时间')
