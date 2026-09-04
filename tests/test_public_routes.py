def test_new_public_home_opens(client, empty_db):
    response = client.get("/v2/")

    assert response.status_code == 200
    assert "Полина Яланская" in response.get_data(as_text=True)
