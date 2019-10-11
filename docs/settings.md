# fastapi部分
## url及其连接密码
API_BASE_URL="/api/v1"  
SECRET_KEY=123456  
ALLOWED_HOSTS='"127.0.0.1", "localhost"'

## 设置安全连接密码
!!! note 
    这部分将来会移到数据库中!  

API_KEY_NAME=auth_token
API_KEY="1234567890123456"


# mongo数据库驱动
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_USER=admin
MONGO_PASS=admin
MONGO_AUTHDB=paperplane
MONGO_DBNAME=paperplane

# 配置collection
SITE_CONFIGS_COLLECTION_NAME=configs

# 如果需要和sentry打通，可以设置sentry dsn
# SENTRY_DSN=''

# 账户token长度
TOKEN_LENGTH=20

# 数据精确度
POINT=2

# 模拟交易引擎模式
# simulation 不获取真实行情进行模拟交易，即时模拟成交
# realtime 获取真实行情并进行模拟交易
ENGINE_MODE=realtime

# 是否开启成交量计算模拟
# 引擎模式为SIMULATION下时，此参数失效
# TODO 暂时没有实现相关功能
VOLUME_SIMULATION=False

# 是否开启账户与持仓信息的验证
VERIFICATION=True

# 引擎撮合速度（秒）
# 引擎模式为SIMULATION下时，此参数失效
# 设置此参数时请参考行情的刷新速度
PERIOD=3

# 报告功能开关参数
REPORT_MODE=True

# mongoDB 参数
ACCOUNT_DB="pt_account"
POSITION_DB="pt_position"
TRADE_DB="pt_trade"
ORDERS_BOOK="pt_orders_book"
MARKET_NAME=""
REPORT="pt_report"

# tushare行情源参数
TUSHARE_TOKEN="12341234123513451345"

# pytdx行情参数
TDX_HOST="114.80.63.5"
TDX_PORT=7709

# 账户初始参数
# 初始资金
ASSETS=1000000.00
# 交易佣金
COST=0.0003
# 印花税
TAX=0.001
# 滑点 暂未实现
SLIPPING=0.01
