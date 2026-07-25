import sqlite3
import pytest
import database.order_items as order_items
from database import orders

@pytest.fixture
def order_items_test_db(tmp_path):
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
    
    
def test_order_items_are_deleted_when_order_is_deleted(order_items_test_db):
    conn = order_items_test_db()
    create_test_product(conn)
    create_test_order(conn)
    create_test_order_item(conn)
    
    conn.commit()
    
    conn.execute("DELETE FROM orders WHERE id = ?", ("order-1",))
    conn.commit()
    conn.close()
    
    check_conn = order_items_test_db()
    
    order_items_count = check_conn.execute("SELECT COUNT (*) FROM order_items WHERE order_id = ?", ("order-1",)).fetchone()[0]
    
    assert order_items_count == 0
    
    product_count = check_conn.execute("SELECT COUNT(*) FROM products WHERE id = ?", ("product-1",)).fetchone()[0]
    
    check_conn.close()
    
    assert product_count == 1
    
    
def test_order_item_keeps_history_when_product_is_deleted(order_items_test_db):
    conn = order_items_test_db()
    create_test_product(conn)
    create_test_order(conn)
    create_test_order_item(conn)
    
    conn.commit()
    
    conn.execute("DELETE FROM products WHERE id = ?", ("product-1",))
    
    conn.commit()
    conn.close()
    
    check_conn = order_items_test_db()
    order_item = check_conn.execute("""
            SELECT product_id, product_name, unit_price, quantity
            FROM order_items
            WHERE order_id = ?
    """, ("order-1",)).fetchone()
    check_conn.close()
    
    assert order_item is not None
    assert order_item["product_id"] is None
    assert order_item["product_name"] == "Башня"
    assert order_item["unit_price"] == 30000
    assert order_item["quantity"] == 1
    
    
def test_insert_order_item_creates_item(order_items_test_db):
    conn = order_items_test_db()
    
    create_test_product(conn)
    create_test_order(conn)
    
    item_id = order_items.insert_order_item(
                conn=conn,
                order_id="order-1",
                product_id="product-1",
                product_name="Башня",
                unit_price=30000,
                quantity=1
    )
    
    conn.commit()
    conn.close()
    
    check_conn = order_items_test_db()
    order_item = check_conn.execute(
            """
            SELECT id, order_id, product_id, product_name, unit_price, quantity
            FROM order_items
            WHERE id = ?
            """,
            (item_id,)
    ).fetchone()
    check_conn.close()
    
    assert order_item is not None
    assert order_item["id"] == item_id
    assert order_item["order_id"] == "order-1"
    assert order_item["product_id"] == "product-1"
    assert order_item["product_name"] == "Башня"
    assert order_item["unit_price"] == 30000
    assert order_item["quantity"] == 1
    
    
def test_insert_order_items_creates_all_items(order_items_test_db):
    conn = order_items_test_db()
    
    create_test_product(
            conn,
            product_id="product-1",
            name="Башня",
            price=30000
        )
    create_test_product(
            conn,
            product_id="product-2",
            name="Чаша",
            price=5000
    )
    
    create_test_order(conn)
    
    items = [
        {
            "product_id": "product-1",
            "product_name": "Башня",
            "unit_price": 30000,
            "quantity": 1
        },
        {
            "product_id": "product-2",
            "product_name": "Чаша",
            "unit_price": 5000,
            "quantity": 2
        }
    ]
    
    item_ids = order_items.insert_order_items(
                conn=conn,
                order_id="order-1",
                items=items
                )
                
    conn.commit()
    conn.close()
    
    check_conn = order_items_test_db()
    saved_items = check_conn.execute("""
            SELECT id, order_id, product_id, product_name, unit_price, quantity
            FROM order_items
            WHERE order_id = ?
            ORDER BY id
    """,
    ("order-1",)
    ).fetchall()
    check_conn.close()
    
    assert len(item_ids) == 2
    assert len(saved_items) == 2
    
    assert saved_items[0]["product_name"] == "Башня"
    assert saved_items[0]["quantity"] == 1
    
    assert saved_items[1]["product_name"] == "Чаша"
    assert saved_items[1]["quantity"] == 2
    
    
def test_insert_order_creates_order(order_items_test_db):
    conn = order_items_test_db()
    
    orders.insert_order(
            conn=conn,
            order_id="order-1",
            customer_name="Денис",
            customer_email="denis@gmail.com",
            customer_phone="55566",
            customer_address="СПБ",
            total=40000,
            status="new"
    )
    
    conn.commit()
    conn.close()
    
    check_conn = order_items_test_db()
    saved_order = check_conn.execute(
            """
                SELECT id, customer_name, customer_email, customer_phone, customer_address, total, status
                FROM orders
                WHERE id = ?
            """,
            ("order-1",)
    ).fetchone()
    check_conn.close()
    
    assert saved_order is not None
    assert saved_order["id"] == "order-1"
    assert saved_order["customer_name"] == "Денис"
    assert saved_order["customer_email"] == "denis@gmail.com"
    assert saved_order["customer_phone"] == "55566"
    assert saved_order["customer_address"] == "СПБ"
    assert saved_order["total"] == 40000
    assert saved_order["status"] == "new"
    

def test_get_order_items_by_order_id_returns_only_requested_order_items(order_items_test_db):
    conn = order_items_test_db()
    
    create_test_product(
        conn=conn,
        product_id='product-1',
        name='Башня',
        price=30000
    )
    create_test_product(
        conn=conn,
        product_id='product-2',
        name='Чаша',
        price=5000
    )
    
    create_test_order(
        conn=conn,
        order_id='order-1'
    )
    create_test_order(
        conn=conn,
        order_id='order-2',
        customer_email='other@email.com'
    )

    create_test_order_item(
        conn=conn,
        order_id='order-1',
        product_id='product-1',
        product_name='Башня',
        unit_price=30000,
        quantity=1
    )
    create_test_order_item(
        conn=conn,
        order_id='order-1',
        product_id='product-2',
        product_name='Чаша',
        unit_price=5000,
        quantity=2
    )
    create_test_order_item(
        conn=conn,
        order_id='order-2',
        product_id='product-2',
        product_name='Чаша',
        unit_price=5000,
        quantity=1
    )

    conn.commit()
    conn.close()

    check_conn = order_items_test_db()
    saved_items = order_items.get_order_items_by_order_id(conn=check_conn, order_id='order-1')
    check_conn.close()

    assert len(saved_items) == 2

    assert saved_items[0]['product_name'] == 'Башня'
    assert saved_items[0]['quantity'] == 1

    assert saved_items[1]['product_name'] == 'Чаша'
    assert saved_items[1]['quantity'] == 2


def test_get_order_by_id_returns_order_with_items(order_items_test_db, monkeypatch):
    conn = order_items_test_db()

    create_test_product(conn)
    create_test_order(conn)
    create_test_order_item(conn)

    conn.commit()
    conn.close()

    monkeypatch.setattr(
        orders,
        'get_db_connection',
        order_items_test_db
    )

    saved_order = orders.get_order_by_id('order-1')

    assert saved_order is not None
    assert saved_order['id'] == 'order-1'
    assert saved_order['total'] == 30000

    assert len(saved_order['items']) == 1
    assert saved_order['items'][0]['product_name'] == 'Башня'
    assert saved_order['items'][0]['unit_price'] == 30000
    assert saved_order['items'][0]['quantity'] == 1


def test_update_order_details_updates_order(order_items_test_db):
    conn = order_items_test_db()

    create_test_order(conn)
    conn.commit()

    is_updated = orders.update_order_details(
        conn=conn,
        order_id='order-1',
        customer_name='Новое имя',
        customer_email='new@mail.com',
        customer_phone='98765',
        customer_address='new address',
        total=60000,
        status='confirmed'
    )

    conn.commit()
    conn.close()

    check_conn = order_items_test_db()
    saved_order = check_conn.execute(
        """
        SELECT
            customer_name, customer_email, customer_phone, customer_address, total, status
        FROM orders
        WHERE id = ?
        """,
        ('order-1',)
    ).fetchone()
    check_conn.close()

    assert is_updated is True
    assert saved_order['customer_name'] == 'Новое имя'
    assert saved_order['customer_email'] == 'new@mail.com'
    assert saved_order['customer_phone'] == '98765'
    assert saved_order['customer_address'] == 'new address'
    assert saved_order['total'] == 60000
    assert saved_order['status'] == 'confirmed'


def test_update_order_item_quantity_updates_requested_item(order_items_test_db):
    conn = order_items_test_db()

    create_test_product(conn)
    create_test_order(conn)
    create_test_order_item(conn)

    conn.commit()

    is_updated = order_items.update_order_item_quantity(
        conn=conn,
        order_id='order-1',
        item_id=1,
        quantity=3
    )

    conn.commit()
    conn.close()

    check_conn = order_items_test_db()
    saved_item = check_conn.execute("SELECT quantity FROM order_items WHERE id = ?", (1, )).fetchone()
    check_conn.close()

    assert is_updated is True
    assert saved_item['quantity'] == 3