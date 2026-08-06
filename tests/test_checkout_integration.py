def test_checkout_creates_order_reserves_product_and_clears_cart(
    empty_db, db_connection, client
):

    conn = db_connection()
    conn.execute(
        "INSERT INTO products (id, name, price) VALUES (?, ?, ?)",
        ("product-1", "Башня", 30000),
    )
    conn.commit()
    conn.close()

    with client.session_transaction() as session:
        session["cart"] = {"product-1": 1}
        session["csrf_token"] = "test-csrf-token"

    response = client.post(
        "/checkout",
        data={
            "csrf_token": "test-csrf-token",
            "customer_name": "Денис",
            "customer_email": "denis@example.com",
            "customer_phone": "+79990000000",
            "customer_address": "spb",
        },
        follow_redirects=False,
    )

    check_conn = db_connection()
    saved_order = check_conn.execute(
        "SELECT id, customer_name, customer_email, total, status FROM orders"
    ).fetchone()
    saved_item = check_conn.execute(
        "SELECT order_id, product_id, product_name, unit_price, quantity FROM order_items"
    ).fetchone()
    saved_product = check_conn.execute(
        "SELECT status FROM products WHERE id = ?", ("product-1",)
    ).fetchone()
    check_conn.close()

    assert response.status_code == 302

    assert saved_order is not None
    assert saved_order["customer_name"] == "Денис"
    assert saved_order["customer_email"] == "denis@example.com"
    assert saved_order["total"] == 30000
    assert saved_order["status"] == "new"

    assert saved_item is not None
    assert saved_item["order_id"] == saved_order["id"]
    assert saved_item["product_id"] == "product-1"
    assert saved_item["product_name"] == "Башня"
    assert saved_item["unit_price"] == 30000
    assert saved_item["quantity"] == 1

    assert saved_product["status"] == "reserved"

    assert response.headers["Location"].endswith(f"/order_success/{saved_order['id']}")

    with client.session_transaction() as session:
        assert session["cart"] == {}


def test_checkout_rejects_creating_partial_order_without_confirmation(
    empty_db, db_connection, client
):

    conn = db_connection()
    conn.execute(
        "INSERT INTO products (id, name, price, status) VALUES (?, ?, ?, ?)",
        ("product-1", "Башня", 30000, "available"),
    )
    conn.execute(
        "INSERT INTO products (id, name, price, status) VALUES (?, ?, ?, ?)",
        ("product-2", "Чаша", 10000, "sold"),
    )
    conn.commit()
    conn.close()

    with client.session_transaction() as session:
        session["cart"] = {
            "product-1": 1,
            "product-2": 1,
        }
        session["csrf_token"] = "test-csrf-token"

    response = client.post(
        "/checkout",
        data={
            "csrf_token": "test-csrf-token",
            "customer_name": "Денис",
            "customer_email": "denis@example.com",
            "customer_phone": "",
            "customer_address": "",
        },
        follow_redirects=False,
    )

    check_conn = db_connection()
    saved_order = check_conn.execute(
        "SELECT id, customer_name, customer_email, total, status FROM orders"
    ).fetchone()
    saved_item = check_conn.execute(
        "SELECT order_id, product_id, product_name, unit_price, quantity FROM order_items"
    ).fetchone()
    saved_products = check_conn.execute("SELECT status FROM products").fetchall()
    check_conn.close()

    assert response.status_code == 302

    assert saved_order is None
    assert saved_item is None

    assert len(saved_products) == 2
    assert saved_products[0]["status"] == "available"
    assert saved_products[1]["status"] == "sold"

    assert response.headers["Location"].endswith("/checkout")

    with client.session_transaction() as session:
        assert session["cart"] == {
            "product-1": 1,
            "product-2": 1,
        }


def test_checkout_creates_partial_order_with_confirmation(
    empty_db, db_connection, client
):

    conn = db_connection()
    conn.execute(
        "INSERT INTO products (id, name, price, status) VALUES (?, ?, ?, ?)",
        ("product-1", "Башня", 30000, "available"),
    )
    conn.execute(
        "INSERT INTO products (id, name, price, status) VALUES (?, ?, ?, ?)",
        ("product-2", "Чаша", 10000, "sold"),
    )
    conn.commit()
    conn.close()

    with client.session_transaction() as session:
        session["cart"] = {
            "product-1": 1,
            "product-2": 1,
        }
        session["csrf_token"] = "test-csrf-token"

    response = client.post(
        "/checkout",
        data={
            "csrf_token": "test-csrf-token",
            "customer_name": "Денис",
            "customer_email": "denis@example.com",
            "customer_phone": "",
            "customer_address": "",
            "confirm_partial_order": "1",
        },
        follow_redirects=False,
    )

    check_conn = db_connection()
    saved_orders = check_conn.execute(
        "SELECT id, customer_name, customer_email, total, status FROM orders"
    ).fetchall()
    saved_items = check_conn.execute(
        "SELECT order_id, product_id, product_name, unit_price, quantity FROM order_items"
    ).fetchall()
    saved_product_rows = check_conn.execute(
        "SELECT id, status FROM products"
    ).fetchall()
    check_conn.close()

    assert response.status_code == 302

    assert len(saved_orders) == 1
    assert len(saved_items) == 1

    saved_order = saved_orders[0]
    saved_item = saved_items[0]

    saved_product_statuses = {
        product["id"]: product["status"] for product in saved_product_rows
    }

    assert saved_order["customer_name"] == "Денис"
    assert saved_order["customer_email"] == "denis@example.com"
    assert saved_order["total"] == 30000
    assert saved_order["status"] == "new"

    assert saved_item["order_id"] == saved_order["id"]
    assert saved_item["product_id"] == "product-1"
    assert saved_item["product_name"] == "Башня"
    assert saved_item["unit_price"] == 30000
    assert saved_item["quantity"] == 1

    assert saved_product_statuses == {
        "product-1": "reserved",
        "product-2": "sold",
    }

    assert response.headers["Location"].endswith(f"/order_success/{saved_order['id']}")

    with client.session_transaction() as session:
        assert session["cart"] == {"product-2": 1}
