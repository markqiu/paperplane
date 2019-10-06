def test_main_engine_start(test_client):
    assert test_client


def test_api_key(test_base_url, test_api_key, test_client, test_acount):
    result = test_client.post(test_base_url + "/account", json=test_acount)
    assert result.status_code == 200
    assert "errors" in result.json()


def test_create_acccount(test_base_url, test_api_key, test_client, test_acount):
    result = test_client.post(test_base_url + f"/account?{test_api_key[0]}={test_api_key[1]}", json=test_acount)
    assert result.status_code == 200
    assert "errors" not in result.json()
    result = test_client.post(test_base_url + f"/account?{test_api_key[0]}={test_api_key[1]}", json=test_acount)
    assert result.status_code == 200
    assert "errors" in result.json()
    assert result.json()["errors"][0] == f"账户{test_acount['account_id']}已存在！"
    test_client.delete(test_base_url + f"/account/{test_acount['account_id']}?{test_api_key[0]}={test_api_key[1]}", json=test_acount)


def test_delete_acccount(test_base_url, test_api_key, test_client, test_acount):
    test_client.post(test_base_url + f"/account?{test_api_key[0]}={test_api_key[1]}", json=test_acount)

    result = test_client.delete(test_base_url + f"/account/{test_acount['account_id']}?{test_api_key[0]}={test_api_key[1]}", json=test_acount)
    assert result.status_code == 200
    assert result.json()
    result = test_client.delete(test_base_url + f"/account/{test_acount['account_id']}?{test_api_key[0]}={test_api_key[1]}", json=test_acount)
    assert result.status_code == 200
    assert not result.json()


def test_list_acccount(test_base_url, test_api_key, test_client, test_acount):
    test_client.post(test_base_url + f"/account?{test_api_key[0]}={test_api_key[1]}", json=test_acount)

    result = test_client.get(test_base_url + f"/account/list?{test_api_key[0]}={test_api_key[1]}", json=test_acount)
    assert result.status_code == 200
    assert len(result.json()) == 1

    test_client.delete(test_base_url + f"/account/{test_acount['account_id']}?{test_api_key[0]}={test_api_key[1]}", json=test_acount)
