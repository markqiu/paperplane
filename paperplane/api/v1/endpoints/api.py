from typing import Union, List

from fastapi import APIRouter, Body, Depends, Path, Query
from fastapi.security.api_key import APIKey
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.exceptions import HTTPException

from ....core.apikey import get_api_key
from ....core.trade.account import (
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
    on_position_init,
)
from ....db.client.mongodb import get_database
from ....models.model import AccountNew, AccountInDB, PositionNew, PositionInDB, Order

router = APIRouter()


@router.post("/account", response_model=bool)
async def account_create(
    account: AccountNew = Body(..., embed=True),
    position: List[PositionNew] = Body(None, embed=True, description="注意持仓数据和market_value必须能够对应上，目前系统未检查。"),
    api_key: APIKey = Depends(get_api_key),
    db_client: AsyncIOMotorDatabase = Depends(get_database),
):
    """创建账户"""
    if not await is_account_exist(account.account_id, db_client):
        if account.market_value != 0:
            if not position:
                raise HTTPException(200, detail="市值不为零的账户必须同时传持仓数据！")
            await on_position_init(account.account_id, position, db_client)
        await create_account(account, db_client)
        return True
    else:
        raise HTTPException(400, f"账户{account.account_id}已存在！")


@router.delete("/account/{account_id}", response_model=bool)
async def account_delete(account_id: str = Path(...), api_key: APIKey = Depends(get_api_key), db_client: AsyncIOMotorDatabase = Depends(get_database)):
    """账户删除"""
    if await is_account_exist(account_id, db_client):
        return await delete_account(account_id, db_client)
    else:
        return False


@router.get("/account/list", response_model=List[AccountInDB])
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


@router.get("/account/{account_id}", response_model=Union[AccountInDB, None])
async def account_query(account_id: str = Path(...), api_key: APIKey = Depends(get_api_key), db_client: AsyncIOMotorDatabase = Depends(get_database)):
    """查询账户信息"""
    return await query_account_one(account_id, db_client)


@router.get("/pos/{account_id}", response_model=List[PositionInDB])
async def position_query(
    account_id: str = Path(...),
    limit: int = Query(20, ge=0, description="限制返回的条数，0=全部"),
    skip: int = Query(0, ge=0),
    api_key: APIKey = Depends(get_api_key),
    db_client: AsyncIOMotorDatabase = Depends(get_database),
):
    """查询持仓信息"""
    poss = []
    async for pos in query_position(account_id, limit, skip, db_client):
        poss.append(pos)
    return poss


@router.get("/order/{account_id}", response_model=List[Order])
async def order_query(
    account_id: str = Path(...),
    limit: int = Query(20, ge=0, description="限制返回的条数，0=全部"),
    skip: int = Query(0, ge=0),
    api_key: APIKey = Depends(get_api_key),
    db_client: AsyncIOMotorDatabase = Depends(get_database),
):
    """查询交割单"""
    orders = []
    async for order in query_orders(account_id, limit, skip, db_client):
        orders.append(order)
    return orders


@router.post("/order/new")
async def order_new(order: Order = Body(...), api_key: APIKey = Depends(get_api_key), db_client: AsyncIOMotorDatabase = Depends(get_database)):
    """接收订单"""
    return await on_orders_arrived(order, db_client)


@router.delete("/order/{order_id}")
async def order_cancel(order_id: str = Path(...), api_key: APIKey = Depends(get_api_key), db_client: AsyncIOMotorDatabase = Depends(get_database)):
    """取消订单"""
    return await on_orders_book_cancel(order_id, db_client)


@router.get("/order/{order_id}/status")
async def order_get_status(order_id: str = Path(...), api_key: APIKey = Depends(get_api_key), db_client: AsyncIOMotorDatabase = Depends(get_database)):
    """查询订单状态"""
    return await query_order_status(order_id, db_client)


@router.get("/liquidation/{account_id}", response_model=bool)
async def liquidation_trigger(account_id: str = Path(...), api_key: APIKey = Depends(get_api_key), db_client: AsyncIOMotorDatabase = Depends(get_database)):
    """清算"""
    if await is_account_exist(account_id, db_client):
        return await on_liquidation(account_id, db_client)
