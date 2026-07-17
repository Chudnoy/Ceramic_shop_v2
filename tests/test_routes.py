import pytest

from app import app
import routes.admin.dashboard as dashboard 

@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()
    
    
def test_admin_login_page_opens(client):
    response = client.get("/admin/login")
    
    page_text = response.get_data(as_text=True)
    
    assert response.status_code == 200
    assert "Вход в админку" in page_text
    
    
def test_admin_redirects_unauthenticated_user_to_login(client):
    
    response = client.get("/admin")
    
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/login")
    
    
def test_admin_redirect_leads_to_login_page(client):
    
    response = client.get("/admin", follow_redirects=True)
    page_text = response.get_data(as_text=True)
    
    assert response.status_code == 200
    assert "Вход в админку" in page_text
    assert len(response.history) == 1
    assert response.history[0].status_code == 302
    
    
def test_authenticated_admin_can_open_dashboard(client, monkeypatch):
    monkeypatch.setattr(
        dashboard,
        "get_admin_stats",
        lambda: {
            "products_count": 3,
            "orders_count": 2,
            "new_orders_count": 1,
            "processing_orders_count": 0,
            "completed_revenue": 5000,
            "total_revenue": 8000
        }
    )
    
    with client.session_transaction() as test_session:
        test_session["is_admin"] = True
        
    response = client.get("/admin")
    page_text = response.get_data(as_text=True)
    
    assert response.status_code == 200
    assert "Админ-панель" in page_text
    assert "8000" in page_text
    
    
def test_logout_removes_admin_session(client):
    with client.session_transaction() as test_session:
        test_session["is_admin"] = True
        test_session["csrf_token"] = "test_token"
        
    response = client.post(
            "/admin/logout",
            data={"csrf_token": "test_token"}
    )
    
    with client.session_transaction() as session_after_logout:
        assert "is_admin" not in session_after_logout
    
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/login")