import pytest

"""账户操作"""


def test_create_account(test_client):
    """创建账户"""
    pytest.skip()


def test_is_account_exist(test_client):
    """账户是否存在"""
    pytest.skip()


def test_delete_account(test_client):
    """账户删除"""
    pytest.skip()


def test_update_account(test_client):
    """订单成交后账户操作"""


def test_on_account_buy(test_client):
    """买入成交后账户操作"""


def test_on_account_sell(test_client):
    """卖出成交后账户操作"""


def test_on_account_liquidation(test_client):
    """账户清算"""


def test_query_account_list(test_client):
    """查询账户列表"""


def test_query_account_one(test_client):
    """查询账户信息"""


"""订单操作"""


def test_on_orders_arrived(test_client):
    """订单到达"""
    pytest.skip()


def test_on_orders_insert(test_client):
    """订单插入"""
    pytest.skip()


def test_is_orders_exist(test_client):
    """查询订单是否存在"""
    pytest.skip()


def test_on_order_update(test_client):
    """订单状态更新"""
    pytest.skip()


def test_on_order_deal(test_client):
    """订单成交处理"""
    pytest.skip()


def test_query_order_status(test_client):
    """查询订单情况"""
    pytest.skip()


def test_query_orders(test_client):
    """查询交割单"""
    pytest.skip()


def test_query_order_one(test_client):
    """查询一条订单数据"""
    pytest.skip()


"""订单薄操作"""


def test_on_orders_book_insert(test_client):
    """订单薄插入订单"""
    pytest.skip()


def test_on_orders_book_cancel(test_client):
    """订单撤单"""
    pytest.skip()


"""持仓操作"""


def test_query_position(test_client):
    """查询所有持仓信息"""
    pytest.skip()


def test_query_position_one(test_client):
    """查询某一只证券的持仓"""
    pytest.skip()


def test_query_position_value(test_client):
    """查询账户市值"""
    pytest.skip()


def test_on_position_init(test_client):
    """初始持仓创建"""
    pytest.skip()


def test_on_position_insert(test_client):
    """持仓增加"""
    pytest.skip()


def test_on_position_update(test_client):
    """订单成交后持仓操作"""
    pytest.skip()


def test_on_position_append(test_client):
    """持仓增长"""
    pytest.skip()


def test_on_position_reduce(test_client):
    """持仓减少"""
    pytest.skip()


def test_on_position_liquidation(test_client):
    """持仓清算"""
    pytest.skip()


def test_on_position_update_price(test_client):
    """更新持仓价格并解除冻结"""
    pytest.skip()


def test_on_position_frozen_cancel(test_client):
    """持仓解除冻结"""
    pytest.skip()


"""验证操作"""


def test_on_front_verification(test_client):
    """订单前置验证"""
    pytest.skip()


def test_account_verification(test_client):
    """订单账户验证"""
    pytest.skip()


def test_position_verification(test_client):
    """订单持仓验证"""
    pytest.skip()


def test_on_buy_frozen(test_client):
    """买入资金冻结"""
    pytest.skip()


def test_on_sell_frozen(test_client):
    """卖出证券冻结"""
    pytest.skip()


def test_on_order_cancel(test_client):
    """取消订单或订单被拒单操作"""
    pytest.skip()


def test_on_buy_cancel(test_client):
    """买入订单取消"""
    pytest.skip()


def test_on_sell_cancel(test_client):
    """卖出取消"""
    pytest.skip()


"""清算操作"""


def test_on_liquidation(test_client):
    """清算"""
    pytest.skip()
