def test_main_engine_start(test_client):
    assert test_client


def test_create_acccount(test_base_url, test_client, test_acount):
    result = test_client.post(test_base_url + "/create", test_acount)
    assert result
