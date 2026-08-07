import pytest

import routes.admin.dashboard as dashboard
import routes.admin.products as admin_products
import routes.main.checkout as checkout_routes


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
            "total_revenue": 8000,
        },
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

    response = client.post("/admin/logout", data={"csrf_token": "test_token"})

    with client.session_transaction() as session_after_logout:
        assert "is_admin" not in session_after_logout

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/login")


def test_invalid_csrf_token_prevents_logout(client):
    with client.session_transaction() as test_session:
        test_session["is_admin"] = True
        test_session["csrf_token"] = "test_token"

    response = client.post("/admin/logout", data={"csrf_token": "wrong_token"})

    with client.session_transaction() as session_after_logout:
        assert session_after_logout["is_admin"] is True

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


@pytest.mark.parametrize(
    "admin_url",
    ["/admin", "/admin/products", "/admin/orders", "/admin/categories", "/admin/tags"],
)
def test_protected_admin_routes_redirect_to_login(client, admin_url):
    response = client.get(admin_url)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/login")


def test_checkout_requires_confirmation_when_cart_contains_unavailable_items(
    client, monkeypatch
):

    with client.session_transaction() as test_session:
        test_session["cart"] = {"product-1": 1, "product-2": 1}
        test_session["csrf_token"] = "test_token"

    monkeypatch.setattr(
        checkout_routes,
        "build_cart_summary",
        lambda _session: {
            "cart": {"product-1": 1, "product-2": 1},
            "available_products": [
                {"id": "product-1", "name": "Башня", "price": 30000}
            ],
            "has_unavailable_items": True,
        },
    )

    def fail_if_create_order_with_items_called(*args, **kwargs):
        raise AssertionError(
            "create_order_with_items не должен вызываться без подтверждения"
        )

    monkeypatch.setattr(
        checkout_routes,
        "create_order_with_items",
        fail_if_create_order_with_items_called,
    )

    response = client.post(
        "/checkout",
        data={
            "customer_name": "Денис",
            "customer_email": "denis@example.com",
            "customer_phone": "",
            "customer_address": "",
            "csrf_token": "test_token",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/checkout")

    with client.session_transaction() as session_after_request:
        assert session_after_request["cart"] == {"product-1": 1, "product-2": 1}


def test_checkout_creates_partial_order_after_confirmation(client, monkeypatch):

    with client.session_transaction() as test_session:
        test_session["cart"] = {"product-1": 1, "product-2": 1}
        test_session["csrf_token"] = "test_token"

    monkeypatch.setattr(
        checkout_routes,
        "build_cart_summary",
        lambda _session: {
            "cart": {"product-1": 1, "product-2": 1},
            "available_products": [
                {"id": "product-1", "name": "Башня", "price": 30000}
            ],
            "has_unavailable_items": True,
        },
    )

    received_order = {}

    def successful_create_order(data, items):
        received_order["data"] = data
        received_order["items"] = items
        return True, "", "order-12345678"

    monkeypatch.setattr(
        checkout_routes, "create_order_with_items", successful_create_order
    )

    response = client.post(
        "/checkout",
        data={
            "customer_name": "Денис",
            "customer_email": "denis@example.com",
            "customer_phone": "",
            "customer_address": "",
            "csrf_token": "test_token",
            "confirm_partial_order": "1",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/order_success/order-12345678")

    assert received_order["items"] == [
        {
            "product_id": "product-1",
            "product_name": "Башня",
            "unit_price": 30000,
            "quantity": 1,
        }
    ]

    with client.session_transaction() as session_after_request:
        assert session_after_request["cart"] == {"product-2": 1}


def test_checkout_preserves_cart_when_order_creation_fails(client, monkeypatch):

    with client.session_transaction() as test_session:
        test_session["cart"] = {"product-1": 1, "product-2": 1}
        test_session["csrf_token"] = "test_token"

    monkeypatch.setattr(
        checkout_routes,
        "build_cart_summary",
        lambda _session: {
            "cart": {"product-1": 1, "product-2": 1},
            "available_products": [
                {"id": "product-1", "name": "Башня", "price": 30000}
            ],
            "has_unavailable_items": True,
        },
    )

    def failed_create_order(data, items):
        return False, "Не удалось создать заказ", None

    monkeypatch.setattr(checkout_routes, "create_order_with_items", failed_create_order)

    response = client.post(
        "/checkout",
        data={
            "customer_name": "Денис",
            "customer_email": "denis@example.com",
            "customer_phone": "",
            "customer_address": "",
            "csrf_token": "test_token",
            "confirm_partial_order": "1",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/cart")

    with client.session_transaction() as session_after_request:
        assert session_after_request["cart"] == {"product-1": 1, "product-2": 1}


def test_checkout_creates_full_order_without_partial_confirmation_when_all_products_available(
    client, monkeypatch
):
    with client.session_transaction() as test_session:
        test_session["cart"] = {"product-1": 1, "product-2": 1}
        test_session["csrf_token"] = "test_token"

    monkeypatch.setattr(
        checkout_routes,
        "build_cart_summary",
        lambda _session: {
            "cart": {"product-1": 1, "product-2": 1},
            "available_products": [
                {"id": "product-1", "name": "Башня", "price": 30000},
                {"id": "product-2", "name": "Чаша", "price": 20000},
            ],
            "has_unavailable_items": False,
        },
    )

    received_order = {}

    def successful_create_order(data, items):
        received_order["data"] = data
        received_order["items"] = items
        return True, "", "order-12345678"

    monkeypatch.setattr(
        checkout_routes, "create_order_with_items", successful_create_order
    )

    response = client.post(
        "/checkout",
        data={
            "customer_name": "Денис",
            "customer_email": "denis@example.com",
            "customer_phone": "",
            "customer_address": "",
            "csrf_token": "test_token",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/order_success/order-12345678")

    assert received_order["items"] == [
        {
            "product_id": "product-1",
            "product_name": "Башня",
            "unit_price": 30000,
            "quantity": 1,
        },
        {
            "product_id": "product-2",
            "product_name": "Чаша",
            "unit_price": 20000,
            "quantity": 1,
        },
    ]

    with client.session_transaction() as session_after_request:
        assert session_after_request["cart"] == {}


@pytest.mark.parametrize(
    "archive_result",
    [
        (True, "", "Башня"),
        (
            False,
            "Нельзя перемещать в архив работу, принадлежащую активному заказу",
            None,
        ),
    ],
    ids=["successful_archive", "failed_archive"],
)
def test_archive_product_route_redirects_to_products_after_success(
    client, monkeypatch, archive_result
):

    with client.session_transaction() as test_session:
        test_session["is_admin"] = True
        test_session["csrf_token"] = "test_token"

    received = {}

    def archive_stub(product_id):
        received["product_id"] = product_id
        return archive_result

    monkeypatch.setattr(
        admin_products, "archive_product_with_order_check", archive_stub
    )

    response = client.post(
        "/admin/products/archive/product-1", data={"csrf_token": "test_token"}
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/products")
    assert received["product_id"] == "product-1"


@pytest.mark.parametrize(
    "restore_result",
    [
        pytest.param((True, "", "Башня"), id="successful_restore"),
        pytest.param(
            (False, "Работа «Башня» уже восстановлена из архива", None),
            id="failed_restore",
        ),
    ],
)
def test_restore_product_route_redirects_to_archive(
    client, monkeypatch, restore_result
):
    with client.session_transaction() as test_session:
        test_session["is_admin"] = True
        test_session["csrf_token"] = "test_token"

    received = {}

    def restore_stub(product_id):
        received["product_id"] = product_id
        return restore_result

    monkeypatch.setattr(admin_products, "restore_archived_product", restore_stub)

    response = client.post(
        "/admin/archived_products/restore/product-1", data={"csrf_token": "test_token"}
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/products/archive")
    assert received["product_id"] == "product-1"
