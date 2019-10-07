import json
from typing import AnyStr, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from starlette.exceptions import HTTPException
from fastapi import APIRouter, Body, Depends, Path, Query
from fastapi.security.api_key import APIKey
from ....core.apikey import get_api_key
from ....core.trade.account import (
    order_generate,
    create_account,
    is_account_exist,
    delete_account,
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
    return "欢迎使用纸飞机模拟交易系统, 请参考README.MD查阅相关文档"


@router.post("/account", response_model=AnyStr, description="创建一个账户，")
async def account_create(account: Account = Body(...), api_key: APIKey = Depends(get_api_key), db_client: AsyncIOMotorDatabase = Depends(get_database)):
    """创建账户"""
    if not await is_account_exist(account.account_id, db_client):
        return await create_account(account, db_client)
    else:
        raise HTTPException(400, f"账户{account.account_id}已存在！")


@router.delete("/account/{account_id}", response_model=bool)
async def account_delete(account_id: str = Path(...), api_key: APIKey = Depends(get_api_key), db_client: AsyncIOMotorDatabase = Depends(get_database)):
    """账户删除"""
    if await is_account_exist(account_id, db_client):
        return await delete_account(account_id, db_client)
    else:
        return False


@router.get("/account/list", response_model=List[Account])
async def account_list(
    limit: int = Query(20, ge=0, description="限制返回的条数，0=全部"),
    skip: int = Query(0, ge=0),
    api_key: APIKey = Depends(get_api_key),
    db_client: AsyncIOMotorDatabase = Depends(get_database),
):
    """获取账户列表"""
    account_list = []
    async for account in query_account_list(limit, skip, db_client):
        account_list.append(account)
    return account_list


@router.get("/account/{account_id}", response_model=Account)
async def account_query(account_id: str = Path(...), api_key: APIKey = Depends(get_api_key), db_client: AsyncIOMotorDatabase = Depends(get_database)):
    """查询账户信息"""
    result = await query_account_one(account_id, db_client)
    if result:
        return result
    else:
        raise HTTPException(status_code=200, detail=f"查无此账户{account_id}")


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
