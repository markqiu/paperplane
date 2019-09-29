import pytest
from starlette.testclient import TestClient
from paperplane.db.client.mongodb import get_database


@pytest.fixture(scope="session")
def test_client():
    """启动服务和撮合引擎"""
    from paperplane.main import app

    with TestClient(app) as test_client:
        yield test_client

    db = get_database()
    db[users_collection_name].delete_many({})
