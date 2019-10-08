import ujson
import asyncio
from paperplane.db.client.mongodb import get_database
from paperplane.core.trade.constants import trade_cl, orders_book_cl, account_cl


def test_main_engine_start(test_client):
    assert test_client


def test_api_key(test_client, test_account):
    result = test_client[0].post(f"account", json=test_account)
    assert result.status_code == 200
    assert "errors" in result.json()
    result = test_client[0].post(f"account?{test_client[1]}={test_client[2]}", json=test_account)
    assert result.status_code == 200
    assert "errors" not in result.json()
    test_client[0].delete(f"account/{test_account['account_id']}?{test_client[1]}={test_client[2]}", json=test_account)


def test_create_acccount(test_client, test_account):
    result = test_client[0].post(f"account?{test_client[1]}={test_client[2]}", json=test_account)
    assert result.status_code == 200
    assert "errors" not in result.json()
    result = test_client[0].post(f"account?{test_client[1]}={test_client[2]}", json=test_account)
    assert result.status_code == 200
    assert "errors" in result.json()
    assert result.json()["errors"][0] == f"账户{test_account['account_id']}已存在！"
    test_client[0].delete(f"account/{test_account['account_id']}?{test_client[1]}={test_client[2]}", json=test_account)


def test_delete_acccount(test_client, test_account):
    test_client[0].post(f"account?{test_client[1]}={test_client[2]}", json=test_account)

    result = test_client[0].delete(f"account/{test_account['account_id']}?{test_client[1]}={test_client[2]}", json=test_account)
    assert result.status_code == 200
    assert result.json()
    result = test_client[0].delete(f"account/{test_account['account_id']}?{test_client[1]}={test_client[2]}", json=test_account)
    assert result.status_code == 200
    assert not result.json()


def test_list_acccount(test_client, test_account):

    json = ujson.load(open("tests/fixtures/account.json"))
    db = get_database()
    asyncio.get_event_loop().run_until_complete(db[account_cl].insert_many(json))
    result = test_client[0].get(f"account/list?{test_client[1]}={test_client[2]}", json=test_account)
    assert result.status_code == 200
    assert len(result.json()) == 20
    result = test_client[0].get(f"account/list?{test_client[1]}={test_client[2]}&skip=20", json=test_account)
    assert result.status_code == 200
    assert len(result.json()) == 4
    result = test_client[0].get(f"account/list?{test_client[1]}={test_client[2]}&skip=20&limit=3", json=test_account)
    assert result.status_code == 200
    assert len(result.json()) == 3
    result = test_client[0].get(f"account/list?{test_client[1]}={test_client[2]}&skip=10&limit=3", json=test_account)
    assert result.status_code == 200
    assert len(result.json()) == 3
    result = test_client[0].get(f"account/list?{test_client[1]}={test_client[2]}&skip=10", json=test_account)
    assert result.status_code == 200
    assert len(result.json()) == 14
    asyncio.get_event_loop().run_until_complete(db[account_cl].delete_many({}))


def test_get_acccount(test_client, test_account):
    test_client[0].post(f"account?{test_client[1]}={test_client[2]}", json=test_account)
    result = test_client[0].get(f"account/{test_account['account_id']}?{test_client[1]}={test_client[2]}")
    assert result.status_code == 200
    assert result.json()["account_id"] == test_account["account_id"]
    test_client[0].delete(f"account/{test_account['account_id']}?{test_client[1]}={test_client[2]}", json=test_account)


def test_pos_query(test_client, test_account):
    result = test_client[0].get(f"pos/{test_account['account_id']}?{test_client[1]}={test_client[2]}")
    assert result.status_code == 200
    assert result.json() == []


def test_order_query(test_client, test_account):
    json = ujson.load(open("tests/fixtures/order.json"))
    db = get_database()
    asyncio.get_event_loop().run_until_complete(db[trade_cl].insert_many(json))
    asyncio.get_event_loop().run_until_complete(db[orders_book_cl].insert_many(json))
    result = test_client[0].get(f"order/{test_account['account_id']}?{test_client[1]}={test_client[2]}")
    assert result.status_code == 200
    i = 0
    for order in result.json():
        assert order["order_id"] == json[i]["order_id"]
        i += 1
    asyncio.get_event_loop().run_until_complete(db[trade_cl].delete_many({}))
    asyncio.get_event_loop().run_until_complete(db[orders_book_cl].delete_many({}))


def test_order_new(test_client, test_account):
    json = ujson.load(open("tests/fixtures/order.json"))
    result = test_client[0].post(f"order/new?{test_client[1]}={test_client[2]}", json=json[0])
    assert result.status_code == 200
    assert result.json() == [False, "账户不存在"]
    test_client[0].post(f"account?{test_client[1]}={test_client[2]}", json=test_account)
    result = test_client[0].post(f"order/new?{test_client[1]}={test_client[2]}", json=json[0])
    assert result.status_code == 200
    assert result.json()[0] == True
    test_client[0].delete(f"account/{test_account['account_id']}?{test_client[1]}={test_client[2]}", json=test_account)


def test_order_cancel(test_client, test_account):
    json = ujson.load(open("tests/fixtures/order.json"))
    db = get_database()
    asyncio.get_event_loop().run_until_complete(db[trade_cl].insert_many(json))
    asyncio.get_event_loop().run_until_complete(db[orders_book_cl].insert_many(json))
    test_client[0].post(f"account?{test_client[1]}={test_client[2]}", json=test_account)
    result = test_client[0].delete(f"order/{json[1]['order_id']}?{test_client[1]}={test_client[2]}")
    assert result.status_code == 200
    assert result.json() == True
    test_client[0].delete(f"account/{test_account['account_id']}?{test_client[1]}={test_client[2]}", json=test_account)
    asyncio.get_event_loop().run_until_complete(db[trade_cl].delete_many({}))
    asyncio.get_event_loop().run_until_complete(db[orders_book_cl].delete_many({}))


def test_order_status_query(test_client, test_account):
    json = ujson.load(open("tests/fixtures/order.json"))
    db = get_database()
    asyncio.get_event_loop().run_until_complete(db[trade_cl].insert_many(json))
    asyncio.get_event_loop().run_until_complete(db[orders_book_cl].insert_many(json))
    result = test_client[0].get(f"order/{json[1]['order_id']}/status?{test_client[1]}={test_client[2]}")
    assert result.status_code == 200
    assert result.json() == [True, json[1]["status"]]
    asyncio.get_event_loop().run_until_complete(db[trade_cl].delete_many({}))
    asyncio.get_event_loop().run_until_complete(db[orders_book_cl].delete_many({}))


def test_liquidation(test_client, test_account):
    json = ujson.load(open("tests/fixtures/order.json"))
    db = get_database()
    asyncio.get_event_loop().run_until_complete(db[trade_cl].insert_many(json))
    asyncio.get_event_loop().run_until_complete(db[orders_book_cl].insert_many(json))
    test_client[0].post(f"account?{test_client[1]}={test_client[2]}", json=test_account)
    result = test_client[0].get(f"liquidation/{json[1]['account_id']}?{test_client[1]}={test_client[2]}")
    assert result.status_code == 200
    assert result.json() == True
    asyncio.get_event_loop().run_until_complete(db[trade_cl].delete_many({}))
    asyncio.get_event_loop().run_until_complete(db[orders_book_cl].delete_many({}))
