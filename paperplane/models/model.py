from pydantic import BaseModel, Schema

from .constant import Status
from .model_mixin import DBModelMixin


class AccountNew(BaseModel):
    """账户数据类"""

    account_id: str = Schema(..., description="外部账户编号, 必须提供，用于对应外部系统的账户")
    available: float = Schema(1000000, description="可用资金, 缺省为100万")
    account_info: str = Schema("", description="账户描述信息")
    market_value: float = Schema(0, description="总市值, 缺省为0，如果不为0，则必须传持仓数据")


class AccountInDB(DBModelMixin, AccountNew):
    """账户数据类"""

    assets: float = Schema(..., description="总资产，缺省等于可用资金+总市值。")


class PositionNew(BaseModel):
    code: str = Schema(..., description="证券代码")
    exchange: str = Schema(..., description="交易所代码")
    volume: float = Schema(..., description="总持仓")
    cost_price: float = Schema(..., description="成本均价")


class PositionInDB(DBModelMixin, PositionNew):
    """持仓数据类"""

    account_id: str = Schema(..., description="外部账户编号, 必须提供，用于对应外部系统的账户")
    available: float = Schema(..., description="可用持仓")
    now_price: float = Schema(..., description="当前价格")
    profit: float = Schema(..., description="收益")


class Order(DBModelMixin):
    """订单数据类"""

    code: str
    exchange: str
    account_id: str  # 账户编号
    order_id: str = ""  # 订单编号
    product: str = ""  # 产品类型 股票、期货等
    order_type: str = ""  # 订单类型 buy、sell等
    price_type: str = ""  # 价格类型 limit、market等
    trade_type: str = ""  # 交易类型 t0、t1等
    order_price: float = 0
    trade_price: float = 0
    volume: float = 0
    traded: float = 0
    status: Status = Status.SUBMITTING.value
    order_date: str = ""
    order_time: str = ""
    error_msg: str = ""
