import pytest
from starlette.testclient import TestClient
from paperplane.db.client.mongodb import get_database
from paperplane.core.trade.constants import account_cl

@pytest.fixture(scope="session")
def test_api_key():
    return "access_token", "1234567890123456"  # 返回 api_key_name, api_key


@pytest.fixture(scope="session")
def test_base_url():
    return "/api/v1"


@pytest.fixture(scope="session")
def test_client():
    """启动服务和撮合引擎"""
    from paperplane.main import app

    with TestClient(app) as test_client:
        yield test_client
        db = get_database()
        db[account_cl].delete_many({})


@pytest.fixture(scope="session")
def test_acount():
    """测试账号"""
    return {
        "account_id": "1234567",
        "assets": 1000000,
        "available": 0,
        "market_value": 0,
        "account_info": "测试账户",
    }
