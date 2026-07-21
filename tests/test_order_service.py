import sqlite3
import pytest

import database.order_items as order_items
import services.order_service as order_service


@pytest.fixture
def order_service_test_db(tmp_path):
    db_path = tmp_path / "test_shop.db"
    
    def get_test_db_connection():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
        
    conn = get_test_db_connection()
    
    conn.execute("""
        CREATE TABLE products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price INTEGER NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE orders (
            id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_phone TEXT,
            customer_address TEXT,
            items TEXT NOT NULL,
            total INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        )
    """)
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
    
    return get_test_db_connection
    
    
def create_test_product(
            conn,
            product_id="product-1",
            name="Башня",
            price=30000
            ):
    conn.execute(
        """
        INSERT INTO products (id, name, price)
        VALUES (?, ?, ?)
        """,
        (product_id, name, price)
    )


def test_create_order_with_items_rolls_back_when_item_insert_fails(order_service_test_db, monkeypatch):
    conn = order_service_test_db()
    
    create_test_product(conn)
    
    conn.commit()
    conn.close()
    
    monkeypatch.setattr(
            order_service,
            "get_db_connection",
            order_service_test_db
    )
    
    def failing_insert_order_items(conn, order_id, items):
        first_item = items[0]
        
        order_items.insert_order_item(
                conn=conn,
                order_id=order_id,
                product_id=first_item["product_id"],
                product_name=first_item["product_name"],
                unit_price=first_item["unit_price"],
                quantity=first_item["quantity"]
        )
        
        raise RuntimeError("Ошибка вставки второй позиции")
        
    monkeypatch.setattr(
            order_service,
            "insert_order_items",
            failing_insert_order_items
    )
    
    data = {
        "customer_name": "Денис",
        "customer_email": "denis@gmail.com",
        "customer_phone": None,
        "customer_address": None,
    }

    items = [
        {
            "product_id": "product-1",
            "product_name": "Башня",
            "unit_price": 30000,
            "quantity": 1,
        },
        {
            "product_id": "product-1",
            "product_name": "Башня",
            "unit_price": 30000,
            "quantity": 1,
        },
    ]
    
    with pytest.raises(RuntimeError, match="Ошибка вставки второй позиции"):
        order_service.create_order_with_items(data, items)
        
    check_conn = order_service_test_db()
    orders_count = check_conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    order_items_count = check_conn.execute("SELECT COUNT(*) FROM order_items").fetchone()[0]
    conn.close()
    
    assert orders_count == 0
    assert order_items_count == 0
    
    
def test_create_order_with_items_creates_order_and_all_items(order_service_test_db, monkeypatch):
    conn = order_service_test_db()

    create_test_product(
        conn,
        product_id="product-1",
        name="Башня",
        price=30000,
    )

    create_test_product(
        conn,
        product_id="product-2",
        name="Чаша",
        price=5000,
    )

    conn.commit()
    conn.close()

    monkeypatch.setattr(
        order_service,
        "get_db_connection",
        order_service_test_db,
    )

    data = {
        "customer_name": "Денис",
        "customer_email": "denis@gmail.com",
        "customer_phone": None,
        "customer_address": None,
    }

    items = [
        {
            "product_id": "product-1",
            "product_name": "Башня",
            "unit_price": 30000,
            "quantity": 1,
        },
        {
            "product_id": "product-2",
            "product_name": "Чаша",
            "unit_price": 5000,
            "quantity": 2,
        },
    ]

    is_created, error_message, order_id = order_service.create_order_with_items(
            data=data,
            items=items,
        )

    check_conn = order_service_test_db()

    saved_order = check_conn.execute(
        """
        SELECT id, customer_name, customer_email, total, status
        FROM orders
        WHERE id = ?
        """,
        (order_id,),
    ).fetchone()

    saved_items = check_conn.execute(
        """
        SELECT product_id, product_name, unit_price, quantity
        FROM order_items
        WHERE order_id = ?
        ORDER BY id
        """,
        (order_id,),
    ).fetchall()

    check_conn.close()

    assert is_created is True
    assert error_message == ""
    assert order_id is not None

    assert saved_order is not None
    assert saved_order["customer_name"] == "Денис"
    assert saved_order["customer_email"] == "denis@gmail.com"
    assert saved_order["total"] == 40000
    assert saved_order["status"] == "new"

    assert len(saved_items) == 2

    assert saved_items[0]["product_id"] == "product-1"
    assert saved_items[0]["product_name"] == "Башня"
    assert saved_items[0]["unit_price"] == 30000
    assert saved_items[0]["quantity"] == 1

    assert saved_items[1]["product_id"] == "product-2"
    assert saved_items[1]["product_name"] == "Чаша"
    assert saved_items[1]["unit_price"] == 5000
    assert saved_items[1]["quantity"] == 2
    
    
def test_build_order_item_list_creates_items_from_available_products():
    cart = {
        "product-1": 1,
        "product-2": 2,
    }

    available_products = [
        {
            "id": "product-1",
            "name": "Башня",
            "price": 30000,
        },
        {
            "id": "product-2",
            "name": "Чаша",
            "price": 5000,
        },
    ]

    items = order_service.build_order_item_list(
        cart=cart,
        available_products=available_products,
    )

    assert items == [
        {
            "product_id": "product-1",
            "product_name": "Башня",
            "unit_price": 30000,
            "quantity": 1,
        },
        {
            "product_id": "product-2",
            "product_name": "Чаша",
            "unit_price": 5000,
            "quantity": 2,
        },
    ]