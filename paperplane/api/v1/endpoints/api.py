import json
from typing import AnyStr
from datetime import timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase

from fastapi import APIRouter, Body, Depends
from ....core.trade.account import (
    order_generate,
    create_account,
    is_account_exist,
    remove_account,
    query_account_list,
    query_account_one,
    query_position,
    query_orders,
    on_orders_arrived,
    on_orders_book_cancel,
    query_order_status,
    on_liquidation,
)
from ....db.client.mongodb import get_database
from ....models.model import Account


router = APIRouter()


@router.get("/")
def index():
    return "欢迎使用模拟交易系统, 请参考README.MD 查阅相关文档"


@router.post("/create", response_model=AnyStr)
async def account_create(
    account: Account = Body(...),
    db_client: AsyncIOMotorDatabase = Depends(get_database),
):
    """创建账户"""
    return await create_account(account, db_client)


@router.post("/delete")
def account_delete():
    """账户删除"""
    rps = {}
    rps["status"] = True

    if request.form.get("token"):
        token = request.form["token"]
        db_client = get_db()
        result = on_account_delete(token, db_client)
        if result:
            rps["data"] = "账户删除成功"
        else:
            rps["status"] = False
            rps["data"] = "删除账户失败"
    else:
        rps["status"] = False
        rps["data"] = "请求参数错误"

    return jsonify(rps)


@router.get("/list")
def account_list():
    """获取账户列表"""
    rps = {}
    rps["status"] = True

    db_client = get_db()
    account_list = query_account_list(db_client)

    if account_list:
        rps["data"] = account_list
    else:
        rps["status"] = False
        rps["data"] = "账户列表为空"

    return jsonify(rps)


@router.post("/account")
def account_query():
    """查询账户信息"""
    rps = {}
    rps["status"] = True

    if request.form.get("token"):
        token = request.form["token"]
        db_client = get_db()
        account = query_account_one(token, db_client)
        if account:
            rps["data"] = account
        else:
            rps["status"] = False
            rps["data"] = "查询账户失败"
    else:
        rps["status"] = False
        rps["data"] = "请求参数错误"

    return jsonify(rps)


@router.post("/pos")
def position_query():
    """查询持仓信息"""
    rps = {}
    rps["status"] = True

    if request.form.get("token"):
        token = request.form["token"]
        db_client = get_db()
        pos = query_position(token, db_client)
        if pos:
            rps["data"] = pos
        else:
            rps["status"] = False
            rps["data"] = "查询持仓失败"
    else:
        rps["status"] = False
        rps["data"] = "请求参数错误"

    return jsonify(rps)


@router.post("/orders")
def orders_query():
    """查询交割单"""
    rps = {}
    rps["status"] = True

    if request.form.get("token"):
        token = request.form["token"]
        db_client = get_db()
        orders = query_orders(token, db_client)
        if orders:
            rps["data"] = orders
        else:
            rps["status"] = False
            rps["data"] = "查询交割单失败"
    else:
        rps["status"] = False
        rps["data"] = "请求参数错误"

    return jsonify(rps)


@router.post("/send")
def order_arrived():
    """接收订单"""
    rps = {}
    rps["status"] = True

    if request.form.get("order"):
        data = request.form["order"]
        data = json.loads(data)
        order = order_generate(data)
        if order:

            db_client = get_db()
            result, msg = on_orders_arrived(order, db_client)
            if result:
                rps["data"] = msg
            else:
                rps["status"] = False
                rps["data"] = msg
        else:
            rps["status"] = False
            rps["data"] = "订单数据错误"
    else:
        rps["status"] = False
        rps["data"] = "请求参数错误"

    return jsonify(rps)


@router.post("/cancel")
def order_cancel():
    """取消订单"""
    rps = {}
    rps["status"] = True

    if request.form.get("token"):
        if request.form.get("order_id"):
            token = request.form["token"]
            order_id = request.form["order_id"]
            db_client = get_db()
            result = on_orders_book_cancel(token, order_id, db_client)
            if result:
                rps["data"] = "撤单成功"
            else:
                rps["status"] = False
                rps["data"] = "撤单失败"
        else:
            rps["status"] = False
            rps["data"] = "请求参数错误"
    else:
        rps["status"] = False
        rps["data"] = "请求参数错误"

    return jsonify(rps)


@router.post("/status")
def get_status():
    """查询订单状态"""
    rps = {}
    rps["status"] = True

    if request.form.get("token"):
        if request.form.get("order_id"):
            token = request.form["token"]
            order_id = request.form["order_id"]
            db_client = get_db()
            result, order_status = query_order_status(token, order_id, db_client)
            if result:
                rps["data"] = order_status
            else:
                rps["status"] = False
                rps["data"] = order_status
        else:
            rps["status"] = False
            rps["data"] = "请求参数错误"
    else:
        rps["status"] = False
        rps["data"] = "请求参数错误"

    return jsonify(rps)


@router.post("/liquidation")
def liquidation():
    """清算"""
    rps = {}
    rps["status"] = True

    if request.form.get("token"):
        token = request.form["token"]
        price_dict = {}
        if request.form.get("price_dict"):
            price_dict = request.form.get("price_dict")
            price_dict = json.loads(price_dict)
        else:
            if not request.form.get("price_dict") == []:
                rps["status"] = False
                rps["data"] = "请求参数错误"
                return jsonify(rps)

        db_client = get_db()
        if on_account_exist(token, db_client):
            result = on_liquidation(db_client, token, price_dict)
            if result:
                rps["data"] = "清算完成"
            else:
                rps["status"] = False
                rps["data"] = "清算失败"

        else:
            rps["status"] = False
            rps["data"] = "账户信息不存在"
    else:
        rps["status"] = False
        rps["data"] = "请求参数错误"

    return jsonify(rps)
