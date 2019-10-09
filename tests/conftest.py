import pytest
import copy
from starlette.testclient import TestClient
from paperplane.db.client.mongodb import get_database
from paperplane.core.trade.constants import account_cl
from paperplane.core.settings import Settings


@pytest.fixture(scope="session")
def test_client():
    """启动服务和撮合引擎"""
    from paperplane.main import app

    with TestClient(app, base_url="http://testserver" + Settings.API_BASE_URL + "/") as test_client:
        yield test_client, Settings.API_KEY_NAME, Settings.API_KEY.get_secret_value()  # 返回 testclient, api_key_name, api_key
        db = get_database()
        db[account_cl].delete_many({})
        del app


@pytest.fixture(scope="session")
def test_account():
    """测试账号"""
    return {"account": {"account_id": "1234567", "available": 1000000.0, "market_value": 0, "account_info": "测试账户"}}


@pytest.fixture(scope="session")
def test_account_with_position(test_account):
    """测试账号"""
    test_account_with_position = copy.deepcopy(test_account)
    test_account_with_position["account"]["market_value"] = 100000
    test_account_with_position["account"]["available"] = 900000
    test_account_with_position["account"]["account_info"] = "测试带持仓账户"
    test_account_with_position["position"] = [{"code": "511880", "exchange": "SH", "volume": 1000, "cost_price": 100}]
    return test_account_with_position
