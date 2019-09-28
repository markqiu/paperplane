from pydantic import BaseModel
from typing import Any

from .constant import Status


class DBData(BaseModel):
    """数据库数据类"""

    db_name: str  # 数据库名称
    db_cl: str  # 表名称
    raw_data: Any  # 原始数据


class Account(BaseModel):
    """账户数据类"""

    account_id: str  # 账户编号
    assets: float = 0  # 总资产
    available: float = 0  # 可用资金
    market_value: float = 0  # 总市值
    account_info: str = ""  # 账户描述信息


class Position(BaseModel):
    """持仓数据类"""

    code: str
    exchange: str
    account_id: str  # 账户编号
    buy_date: str = 0  # 买入日期
    volume: float = 0  # 总持仓
    available: float = 0  # 可用持仓
    buy_price: float = 0  # 买入均价
    now_price: float = 0  # 当前价格
    profit: float = 0  # 收益

    def __post_init__(self):
        """"""
        self.pt_symbol = f"{self.code}.{self.exchange}"


class Order(BaseModel):
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

    def __post_init__(self):
        """"""
        self.pt_symbol = f"{self.code}.{self.exchange}"
