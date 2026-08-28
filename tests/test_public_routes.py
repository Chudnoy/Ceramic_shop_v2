def test_new_public_home_opens(client):
    response = client.get("/v2/")

    assert response.status_code == 200
    assert "Новый Ceramic Shop" in response.get_data(as_text=True)
