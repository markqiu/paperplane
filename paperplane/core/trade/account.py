import time
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from .constants import account_cl, orders_book_cl, position_cl, trade_cl
from ..settings import Settings
from ...models.constant import Status, OrderType, TradeType
from ...models.model import AccountNew, AccountInDB, PositionNew, PositionInDB, Order

"""账户操作"""


async def create_account(account: AccountNew, db: AsyncIOMotorDatabase) -> str:
    """创建账户"""
    account = AccountInDB(**account.dict(), assets=account.market_value + account.available)
    result = await db[account_cl].insert_one(account.dict())
    return str(result.inserted_id)


async def is_account_exist(account_id: str, db: AsyncIOMotorDatabase):
    """账户是否存在"""
    account = await query_account_one(account_id, db)
    if account:
        return True
    else:
        return False


async def delete_account(account_id: str, db: AsyncIOMotorDatabase):
    """账户删除"""
    try:
        async with await db.client.start_session() as session:
            async with session.start_transaction():
                await db[orders_book_cl].delete_many({"account_id": account_id}, session=session)
                await db[account_cl].delete_many({"account_id": account_id}, session=session)
                await db[position_cl].delete_many({"account_id": account_id}, session=session)
                await db[trade_cl].delete_many({"account_id": account_id}, session=session)
                return True
    except Exception:
        logging.error("删除账户发生错误，请检查!", exc_info=True)
        return False


async def update_account(order: Order, db: AsyncIOMotorDatabase):
    """订单成交后的账户操作"""
    account = await query_account_one(order.account_id, db)
    pos_val = await query_position_value(order.account_id, db)

    if order.order_type == OrderType.BUY.value:
        await on_account_buy(account, order, pos_val, db)
    else:
        await on_account_sell(account, order, pos_val, db)


async def on_account_buy(account: AccountInDB, order: Order, pos_val: float, db: AsyncIOMotorDatabase):
    """买入成交后账户操作"""
    frozen_all = account.assets - account.available - account.market_value
    frozen = (order.volume * order.order_price) * (1 + Settings.COST)
    pay = (order.traded * order.trade_price) * (1 + Settings.COST)

    available = account.available + frozen - pay
    frozen_all = frozen_all - frozen
    assets = available + pos_val + frozen_all
    result = await db[account_cl].update_one(
        {"account_id": account.account_id},
        {"$set": {"available": round(available, Settings.POINT), "assets": round(assets, Settings.POINT), "market_value": round(pos_val, Settings.POINT)}},
    )
    return result


async def on_account_sell(account: AccountInDB, order: Order, pos_val: float, db: AsyncIOMotorDatabase):
    """卖出成交后账户操作"""
    frozen = account.assets - account.available - account.market_value
    order_val = order.traded * order.trade_price
    cost = order_val * Settings.COST
    tax = order_val * Settings.TAX
    available = account.available + order_val - cost - tax
    assets = available + pos_val + frozen

    result = await db[account_cl].update_one(
        {"account_id": account.account_id},
        {"$set": {"available": round(available, Settings.POINT), "assets": round(assets, Settings.POINT), "market_value": round(pos_val, Settings.POINT)}},
    )
    return result


async def on_account_liquidation(account_id: str, db: AsyncIOMotorDatabase):
    """账户清算"""
    account = await query_account_one(account_id, db)
    pos_val = await query_position_value(account_id, db)

    # 解除冻结
    available = account.assets - account.market_value
    assets = available + pos_val

    result = await db[account_cl].update_one(
        {"account_id": account.account_id},
        {"$set": {"available": round(available, Settings.POINT), "assets": round(assets, Settings.POINT), "market_value": round(pos_val, Settings.POINT)}},
    )
    return result


async def query_account_list(limit: int, skip: int, db: AsyncIOMotorDatabase):
    """查询账户列表"""
    cursor = db[account_cl].find({}, limit=limit, skip=skip)
    async for account in cursor:
        yield account


async def query_account_one(account_id: str, db: AsyncIOMotorDatabase) -> AccountInDB:
    """查询账户信息"""
    if account_id:
        account_dict = await db[account_cl].find_one({"account_id": account_id})
        return AccountInDB(**account_dict) if account_dict else None
    else:
        raise ValueError("account_id不能为空")


"""订单操作"""


async def on_orders_arrived(order: Order, db: AsyncIOMotorDatabase):
    """订单到达"""
    # 接收订单前的验证
    if Settings.VERIFICATION:
        result, msg = await on_front_verification(order, db)
        if not result:
            return result, msg

    return await on_orders_book_insert(order, db)


async def on_orders_insert(order: Order, db: AsyncIOMotorDatabase):
    """订单插入"""
    account_id = order.account_id
    order.status = Status.NOTTRADED.value
    try:
        await db[trade_cl].replace_one({"order_id": order.order_id, "account_id": account_id}, order.dict(), upsert=True)
        return True, order.order_id
    except Exception as e:
        return False, f"交易表新增订单失败{e}"


async def is_orders_exist(order_id: str, db: AsyncIOMotorDatabase):
    """查询订单是否存在"""
    result = await db[trade_cl].find_one({"order_id": order_id})
    if result:
        return True
    else:
        return False


async def on_order_update(order: Order, db: AsyncIOMotorDatabase):
    """订单状态更新"""
    result, order_old = await query_order_one(order.order_id, db)
    result = await db[trade_cl].update_many(
        {"order_id": order.order_id, "account_id": order.account_id},
        {
            "$set": {
                "status": order.status,
                "trade_type": order.trade_type,
                "trade_price": order.trade_price,
                "traded": (order.traded + order_old["traded"]),
                "error_msg": order.error_msg,
            }
        },
    )
    if result:
        return result
    else:
        return False


async def on_order_deal(order: Order, db: AsyncIOMotorDatabase):
    """订单成交事件总入口，订单成交处理"""
    # 持仓处理
    await on_position_update(order, db)

    # 账户处理
    await update_account(order, db)

    if order.volume == order.traded:
        order.status = Status.ALLTRADED.value
    else:
        order.status = Status.PARTTRADED.value

    await on_order_update(order, db)


async def query_order_status(order_id: str, db: AsyncIOMotorDatabase):
    """查询订单情况"""
    order = await db[trade_cl].find_one({"order_id": order_id})
    if order:
        return True, order["status"]
    else:
        return False, "无此订单"


async def query_orders(account_id: str, limit: int, skip: int, db: AsyncIOMotorDatabase):
    """查询交割单"""
    async for order in db[trade_cl].find({"account_id": account_id}, limit=limit, skip=skip):
        yield order


async def query_order_one(order_id: str, db: AsyncIOMotorDatabase):
    """查询一条订单数据"""
    order = await db[trade_cl].find_one({"order_id": order_id})
    if order:
        return True, order
    else:
        return False, "无此订单"


"""订单薄操作"""


async def on_orders_book_insert(order: Order, db: AsyncIOMotorDatabase):
    """订单薄插入订单"""
    order.order_id = str(time.time())
    order.status = order.status.value
    result = await db[orders_book_cl].insert_one(order.dict())
    if result:
        return await on_orders_insert(order, db)
    else:
        return False, "订单薄新增订单失败"


async def on_orders_book_cancel(order_id: str, db: AsyncIOMotorDatabase):
    """订单撤单"""
    result = await db[orders_book_cl].delete_one({"order_id": order_id})
    if result.deleted_count:
        result, order = await query_order_one(order_id, db)
        if result:
            order = Order(**order)
            order.status = Status.CANCELLED.value
            await on_order_cancel(order, db)
        return True
    else:
        return False


"""持仓操作"""


async def query_position(account_id: str, limit: int, skip: int, db: AsyncIOMotorDatabase):
    """查询所有持仓信息"""
    async for pos in db[position_cl].find({"account_id": account_id}, limit=limit, skip=skip):
        yield pos


async def query_position_one(account_id: str, symbol: str, exchange: str, db: AsyncIOMotorDatabase):
    """查询某一只证券的持仓"""
    return await db[position_cl].find_one({"account_id": account_id, "code": symbol, "exchange": exchange})


async def query_position_value(account_id: str, db: AsyncIOMotorDatabase):
    """查询账户市值"""
    value = 0
    async for pos in query_position(account_id, 0, 0, db):
        value += pos["volume"] * pos["now_price"]
    return value


async def on_position_init(account_id: str, pos_list: List[PositionNew], db: AsyncIOMotorDatabase):
    """初始持仓创建"""
    from paperplane.core.event.manager import me

    pos_list_to_db = []
    for pos in pos_list:
        hq = me._market.hq_client.get_realtime_data(f"{pos.code}.{pos.exchange}")
        if hq is not None:
            now_price = float(hq.loc[0, "price"])
            profit = now_price - pos.cost_price
        else:
            now_price = pos.cost_price
            profit = 0

        pos_list_to_db.append(
            PositionInDB(
                code=pos.code,
                exchange=pos.exchange,
                account_id=account_id,
                volume=pos.volume,
                available=pos.volume,
                cost_price=pos.cost_price,
                now_price=now_price,
                profit=profit,
            ).dict()
        )
    return await db[position_cl].insert_many(pos_list_to_db)


async def on_position_insert(order: Order, cost: float, db: AsyncIOMotorDatabase):
    """持仓增加"""
    profit = cost * -1
    available = order.traded
    if order.trade_type == TradeType.T_PLUS1.value:
        available = 0

    pos = PositionInDB(
        code=order.code,
        exchange=order.exchange,
        account_id=order.account_id,
        volume=order.traded,
        available=available,
        cost_price=order.trade_price,
        now_price=order.trade_price,
        profit=profit,
    )
    return await db[position_cl].insert_one(pos.dict())


async def on_position_update(order: Order, db: AsyncIOMotorDatabase):
    """订单成交后持仓操作"""
    if order.order_type == OrderType.BUY.value:
        await on_position_append(order, db)
    else:
        await on_position_reduce(order, db)


async def on_position_append(order: Order, db: AsyncIOMotorDatabase):
    """持仓增长"""
    pos_o = await query_position_one(order.account_id, order.code, order.exchange, db)
    cost = order.volume * order.trade_price * Settings.COST
    if pos_o:
        volume = pos_o["volume"] + order.traded
        now_price = order.trade_price
        profit = (order.trade_price - pos_o["now_price"]) * pos_o["volume"] + pos_o["profit"] - cost
        available = pos_o["available"] + order.traded

        if order.trade_type == TradeType.T_PLUS1.value:
            available = 0

        buy_price = round(((pos_o["volume"] * pos_o["now_price"]) + (order.traded * order.trade_price)) / volume, 2)

        return await db[position_cl].update_one(
            {"code": order.code, "exchange": order.exchange, "account_id": order.account_id},
            {
                "$set": {
                    "volume": round(volume, Settings.POINT),
                    "available": round(available, Settings.POINT),
                    "buy_price": round(buy_price, Settings.POINT),
                    "now_price": round(now_price, Settings.POINT),
                    "profit": round(profit, Settings.POINT),
                }
            },
        )
    else:
        return await on_position_insert(order, cost, db)


async def on_position_reduce(order: Order, db: AsyncIOMotorDatabase):
    """持仓减少"""
    result, pos_o = await query_position_one(order.account_id, order.code, order.exchange, db)
    volume = pos_o["volume"] - order.volume
    now_price = order.trade_price
    cost = order.volume * order.trade_price * Settings.COST
    tax = order.volume * order.trade_price * Settings.TAX
    profit = (order.trade_price - pos_o["now_price"]) * pos_o["volume"] + pos_o["profit"] - cost - tax

    return await db[position_cl].update_one(
        {"code": order.code, "exchange": order.exchange, "account_id": order.account_id},
        {"$set": {"volume": round(volume, Settings.POINT), "now_price": round(now_price, Settings.POINT), "profit": round(profit, Settings.POINT)}},
    )


async def on_position_liquidation(account_id, db: AsyncIOMotorDatabase):
    """持仓清算"""
    from paperplane.core.event.manager import me

    async for pos in query_position(account_id, 0, 0, db):
        hq = me._market.hq_client.get_realtime_data(f"{pos['code']}.{pos['exchange']}")
        if hq is not None:
            now_price = float(hq.loc[0, "price"])
            # 更新收盘行情
            await on_position_update_price(pos, now_price, db)
        # 解除账户冻结
        await on_position_frozen_cancel(account_id, pos, db)


async def on_position_update_price(pos: dict, price: float, db: AsyncIOMotorDatabase):
    """更新持仓价格并解除冻结"""
    volume = pos["volume"]
    if volume:
        profit = (price - pos["now_price"]) * pos["volume"] + pos["profit"]

        return await db[position_cl].update_many(
            {"code": pos["code"], "exchange": pos["exchange"]},
            {"$set": {"now_price": round(price, Settings.POINT), "profit": round(profit, Settings.POINT), "available": volume}},
        )


async def on_position_frozen_cancel(account_id: str, pos: dict, db: AsyncIOMotorDatabase):
    """持仓解除冻结"""
    volume = pos["volume"]
    if volume:
        await db[position_cl].update_one({"code": pos["code"], "exchange": pos["exchange"], "account_id": account_id}, {"$set": {"available": pos["volume"]}})


"""验证操作"""


async def on_front_verification(order: Order, db: AsyncIOMotorDatabase):
    """订单前置验证"""
    # 验证市场是否开启
    if not Settings.MARKET_NAME:
        return False, "交易市场关闭"

    # 验证账户是否存在
    if not await is_account_exist(order.account_id, db):
        return False, "账户不存在"

    if order.order_type == OrderType.BUY.value:
        return await account_verification(order, db)
    else:
        return await position_verification(order, db)


async def account_verification(order: Order, db: AsyncIOMotorDatabase):
    """订单账户验证"""
    money_need = order.volume * order.order_price * (1 + Settings.COST)
    account = await query_account_one(order.account_id, db)

    if account.available >= money_need:
        await on_buy_frozen(account, money_need, db)
        return True, ""
    else:
        return False, "账户资金不足"


async def position_verification(order: Order, db: AsyncIOMotorDatabase):
    """订单持仓验证"""
    pos_need = order.volume
    result, pos = await query_position_one(order.account_id, order.code, order.exchange, db)

    if result:
        if pos["available"] >= pos_need:
            await on_sell_frozen(pos, order.volume, db)
            return True, ""
        else:
            return False, "可用持仓不足"
    else:
        return False, "无可用持仓"


async def on_buy_frozen(account: AccountInDB, pay: float, db: AsyncIOMotorDatabase):
    """买入资金冻结"""
    available = account.available - pay
    return await db[account_cl].update_one({"account_id": account.account_id}, {"$set": {"available": available}})


async def on_sell_frozen(pos, vol: float, db: AsyncIOMotorDatabase):
    """卖出证券冻结"""
    available = pos["available"] - vol
    return await db[position_cl].update_one(
        {"account_id": pos["account_id"], "code": pos["code"], "exchange": pos["exchange"]}, {"$set": {"available": available}}
    )


async def on_order_cancel(order: Order, db: AsyncIOMotorDatabase):
    """取消订单或订单被拒单操作"""
    await on_order_update(order, db)

    if order.order_type == OrderType.BUY.value:
        return await on_buy_cancel(order, db)
    else:
        return await on_sell_cancel(order, db)


async def on_buy_cancel(order: Order, db: AsyncIOMotorDatabase):
    """买入订单取消"""
    pay = (order.volume - order.traded) * order.order_price * (1 + Settings.COST)
    account = await query_account_one(order.account_id, db)
    available = account.available + pay
    return await db[account_cl].update_one({"account_id": account.account_id}, {"$set": {"available": available}})


async def on_sell_cancel(order: Order, db: AsyncIOMotorDatabase):
    """卖出取消"""
    result, pos = await query_position_one(order.account_id, order.code, order.exchange, db)
    available = pos["available"] + order.volume - order.traded
    return await db[position_cl].update_one(
        {"account_id": pos["account_id"], "code": pos["code"], "exchange": pos["exchange"]}, {"$set": {"available": available}}
    )


"""清算操作"""


async def on_liquidation(account_id: str, db) -> bool:
    """清算"""
    # 更新所有持仓最新价格和冻结证券
    await on_position_liquidation(account_id, db)

    # 更新账户市值和冻结资金
    await on_account_liquidation(account_id, db)

    return True
