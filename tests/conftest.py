import pytest
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


@pytest.fixture(scope="session")
def test_account():
    """测试账号"""
    return {"account_id": "1234567", "assets": 1000000, "available": 1000000.0, "market_value": 0, "account_info": "测试账户"}
