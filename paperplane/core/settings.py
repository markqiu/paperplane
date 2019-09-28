from typing import Set

from dotenv import load_dotenv
from pydantic import BaseSettings, Schema
from pydantic.error_wrappers import ValidationError

from ..models.constant import EngineMode


class SettingsModel(BaseSettings):
    API_BASE_URL: str

    JWT_TOKEN_PREFIX: str = "Token"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # one week

    MAX_CONNECTIONS_COUNT: int
    MIN_CONNECTIONS_COUNT: int
    SECRET_KEY: str

    SENTRY_DSN: str = Schema(None, description="如果需要和sentry打通，可以设置sentry dsn")

    ALLOWED_HOSTS: Set[str] = set()

    MONGO_DBNAME: str
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_USER: str
    MONGO_PASS: str
    MONGO_AUTHDB: str
    SITE_CONFIGS_COLLECTION_NAME: str

    CLIENT_API_KEY: str = Schema(None, description="暂时使用的clientid，用于获取调用api权限的凭证")
    CLIENT_ID: str = Schema(None, description="暂时使用的clientid，用于获取调用api权限的凭证")
    SERVER_DOMAIN: str = Schema(None, description="服务器的domain，用于设置cookie")

    # 账户token长度
    TOKEN_LENGTH = 20

    # 数据精确度
    POINT = 2

    # 模拟交易引擎模式
    # SIMULATION 不获取真实行情进行模拟交易，即时模拟成交
    # REALTIME 获取真实行情并进行模拟交易
    ENGINE_MODE: EngineMode

    # 是否开启成交量计算模拟
    # 引擎模式为SIMULATION下时，此参数失效
    # TODO 暂时没有实现相关功能
    VOLUME_SIMULATION: bool

    # 是否开启账户与持仓信息的验证
    VERIFICATION: bool

    # 引擎撮合速度（秒）
    # 引擎模式为SIMULATION下时，此参数失效
    # 设置此参数时请参考行情的刷新速度
    PERIOD: int = 3

    # 报告功能开关参数
    REPORT_MODE: bool

    # mongoDB 参数
    ACCOUNT_DB = "pt_account"
    POSITION_DB = "pt_position"
    TRADE_DB = "pt_trade"
    ORDERS_BOOK = "pt_orders_book"
    MARKET_NAME = ""
    REPORT = "pt_report"

    # tushare行情源参数
    TUSHARE_TOKEN = "34467743d1e895f3e48b884958b379b1f1f58eae3b4511f48383ba0a"

    # pytdx行情参数
    TDX_HOST = "114.80.63.5"
    TDX_PORT = 7709

    # 账户初始参数
    ASSETS = 1000000.00  # 初始资金
    COST = 0.0003  # 交易佣金
    TAX = 0.001  # 印花税
    SLIPPING = 0.01  # 滑点 暂未实现

    class Config:
        env_prefix = ""
        case_insensitive = True


# 加载配置文件.env
try:
    load_dotenv()
    Settings = SettingsModel()
except ValidationError as e:
    raise RuntimeError(f"配置文件解析错误，请检查配置文件。\n详细错误如下\n：{e}")
print(f"服务器配置如下：\n {Settings.to_string(pretty=True)}")