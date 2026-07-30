import sqlite3
import pytest
import database.orders as orders


@pytest.fixture
def orders_test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_shop.db"
    
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT "available"
        )
    """)
    conn.execute("""CREATE TABLE orders (
                 id TEXT PRIMARY KEY,
                 customer_name TEXT NOT NULL,
                 customer_email TEXT NOT NULL,
                 customer_phone TEXT,
                 customer_address TEXT,
                 total INTEGER NOT NULL,
                 status TEXT NOT NULL DEFAULT 'new',
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )""")
    conn.execute("""
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            product_id TEXT,
            product_name TEXT NOT NULL,
            unit_price INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            
            FOREIGN KEY (order_id)
                REFERENCES orders(id)
                ON DELETE CASCADE,
            
            FOREIGN KEY (product_id)
                REFERENCES products(id)
                ON DELETE SET NULL
        )
    """)
    conn.commit()
    conn.close()
    
    def get_test_db_connection():
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn
    
    monkeypatch.setattr(
            orders,
            "get_db_connection",
            get_test_db_connection
    )
    
    return get_test_db_connection
    
    
def create_test_product(
            conn,
            product_id="product-1",
            name="Башня",
            price=30000,
            status="available"
            ):
    conn.execute(
        """
        INSERT INTO products (id, name, price, status)
        VALUES (?, ?, ?, ?)
        """,
        (product_id, name, price, status)
    )
    
    
def create_test_order(
            conn,
            order_id="order-1",
            customer_name="Денис",
            customer_email="denis@gmail.com",
            customer_phone=None,
            customer_address=None,
            total=30000,
            status="new"
            ):
    conn.execute(
        """
        INSERT INTO orders (id, customer_name, customer_email, customer_phone, customer_address, total, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (order_id, customer_name, customer_email, customer_phone, customer_address, total, status)
    )
    
    
def create_test_order_item(
            conn,
            order_id="order-1",
            product_id="product-1",
            product_name="Башня",
            unit_price=30000,
            quantity=1
            ):
    conn.execute(
        """
        INSERT INTO order_items (order_id, product_id, product_name, unit_price, quantity)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order_id, product_id, product_name, unit_price, quantity)
    )
    
    
def test_update_order_status_updates_when_status_matches(orders_test_db):
    
    conn = orders_test_db()
    create_test_order(conn)
    
    result = orders.update_order_status(
            conn=conn,
            order_id="order-1",
            new_status="confirmed",
            expected_status="new"
            )
    conn.commit()
    conn.close()
    
    check_conn = orders_test_db()
    order = check_conn.execute("SELECT * FROM orders WHERE id = ?", ("order-1",)).fetchone()
    check_conn.close()
    
    assert result is True
    assert order is not None
    assert order["status"] == "confirmed"
    
    
def test_update_order_status_does_not_update_when_status_does_not_match(orders_test_db):
    conn = orders_test_db()
    create_test_order(conn, status="completed")
    
    result = orders.update_order_status(
            conn=conn,
            order_id="order-1",
            new_status="canceled",
            expected_status="new"
            )
    conn.commit()
    conn.close()
    
    check_conn = orders_test_db()
    order = check_conn.execute("SELECT * FROM orders WHERE id = ?", ("order-1",)).fetchone()
    check_conn.close()
    
    assert result is False
    assert order is not None
    assert order["status"] == "completed"


def test_has_active_order_for_product_returns_true_for_confirmed_order(
        orders_test_db
):
    conn = orders_test_db()

    create_test_product(
        conn=conn,
        product_id="product-1",
        status="reserved"
    )

    create_test_order(
        conn=conn,
        order_id="order-1",
        status="confirmed"
    )

    create_test_order_item(
        conn=conn,
        order_id="order-1",
        product_id="product-1"
    )

    conn.commit()

    result = orders.has_active_order_for_product(
        conn=conn,
        product_id="product-1"
    )

    conn.close()

    assert result is True


def test_has_active_order_for_product_returns_false_for_canceled_order(
        orders_test_db
):
    conn = orders_test_db()

    create_test_product(
        conn=conn,
        product_id="product-1",
        status="available"
    )

    create_test_order(
        conn=conn,
        order_id="order-1",
        status="canceled"
    )

    create_test_order_item(
        conn=conn,
        order_id="order-1",
        product_id="product-1"
    )

    conn.commit()

    result = orders.has_active_order_for_product(
        conn=conn,
        product_id="product-1"
    )

    conn.close()

    assert result is False
    
    
@pytest.mark.parametrize(
    "order_status",
    ["new", "confirmed"]
)
def test_has_active_order_for_product_returns_true_for_active_statuses(orders_test_db, order_status):
    conn = orders_test_db()
    create_test_product(conn=conn)
    create_test_order(conn=conn, status=order_status)
    create_test_order_item(conn=conn)
    conn.commit()
    conn.close()
    
    check_conn = orders_test_db()
    result = orders.has_active_order_for_product(conn=check_conn, product_id="product-1")
    conn.close()
    
    assert result is True
    
    
@pytest.mark.parametrize(
    "order_status",
    ["completed", "canceled"]
)
def test_has_active_order_for_product_returns_false_for_inactive_statuses(orders_test_db, order_status):
    conn = orders_test_db()
    create_test_product(conn=conn)
    create_test_order(conn=conn, status=order_status)
    create_test_order_item(conn=conn)
    conn.commit()
    conn.close()
    
    check_conn = orders_test_db()
    result = orders.has_active_order_for_product(conn=check_conn, product_id="product-1")
    check_conn.close()
    
    assert result is False
    
    
def test_has_active_order_for_product_ignores_active_order_for_another_product(orders_test_db):
    conn = orders_test_db()

    create_test_product(
        conn=conn,
        product_id="product-1"
    )
    create_test_product(
        conn=conn,
        product_id="product-2"
    )

    create_test_order(
        conn=conn,
        order_id="order-1",
        status="new"
    )

    create_test_order_item(
        conn=conn,
        order_id="order-1",
        product_id="product-2"
    )

    conn.commit()
    conn.close()

    check_conn = orders_test_db()
    result = orders.has_active_order_for_product(
        conn=check_conn,
        product_id="product-1"
    )
    check_conn.close()

    assert result is False