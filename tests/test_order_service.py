import pytest

import database.order_items as order_items
import services.order_service as order_service
    
    
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


def create_test_order_with_item(
        conn,
        order_status="new",
        product_status="reserved",
        order_id="order-1",
        product_id="product-1",
        product_name="Башня",
        unit_price=30000,
        quantity=1
):
    create_test_product(
        conn=conn,
        product_id=product_id,
        name=product_name,
        price=unit_price,
        status=product_status
    )
    create_test_order(
        conn=conn,
        order_id=order_id,
        total=unit_price * quantity,
        status=order_status
    )
    create_test_order_item(
        conn=conn,
        order_id=order_id,
        product_id=product_id,
        product_name=product_name,
        unit_price=unit_price,
        quantity=quantity
    )


def get_saved_order(conn, order_id="order-1"):
    return conn.execute(
        "SELECT * FROM orders WHERE id = ?",
        (order_id,)
    ).fetchone()


def get_saved_product(conn, product_id="product-1"):
    return conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()


def make_checkout_data():
    return {
        "customer_name": "Денис",
        "customer_email": "denis@gmail.com",
        "customer_phone": None,
        "customer_address": None,
    }


def make_order_item(
        product_id,
        product_name,
        unit_price,
        quantity=1
):
    return {
        "product_id": product_id,
        "product_name": product_name,
        "unit_price": unit_price,
        "quantity": quantity,
    }


def test_create_order_with_items_rolls_back_when_item_insert_fails(empty_db, db_connection, monkeypatch):
    conn = db_connection()
    
    create_test_product(conn)
    
    conn.commit()
    conn.close()
    
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
    
    items = [
        make_order_item("product-1", "Башня", 30000),
        make_order_item("product-1", "Башня", 30000),
    ]
    
    with pytest.raises(RuntimeError, match="Ошибка вставки второй позиции"):
        order_service.create_order_with_items(make_checkout_data(), items)
        
    check_conn = db_connection()
    orders_count = check_conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    order_items_count = check_conn.execute("SELECT COUNT(*) FROM order_items").fetchone()[0]
    check_conn.close()
    
    assert orders_count == 0
    assert order_items_count == 0
    
    
def test_create_order_with_items_creates_order_and_all_items(empty_db, db_connection):
    conn = db_connection()

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

    items = [
        make_order_item("product-1", "Башня", 30000),
        make_order_item("product-2", "Чаша", 5000, quantity=2),
    ]

    is_created, error_message, order_id = order_service.create_order_with_items(
            data=make_checkout_data(),
            items=items,
        )

    check_conn = db_connection()

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


def test_update_order_with_items_updates_order_and_all_items(empty_db, db_connection):
    conn = db_connection()

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
        order_id='order-1',
        total=40000
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

    conn.commit()

    saved_item_rows = conn.execute("SELECT id, product_id FROM order_items WHERE order_id = ? ORDER BY id", ('order-1',)).fetchall()

    first_item_id = saved_item_rows[0]['id']
    second_item_id = saved_item_rows[1]['id']

    conn.close()

    data = {
        'name': 'Новое имя',
        'email': 'new@mail.com',
        'phone': '98765',
        'address': 'new address',
        'items': [
            {
                'id': first_item_id,
                'quantity': 2
            },
            {
                'id': second_item_id,
                'quantity': 3
            }
        ],
        'total': 75000,
    }

    is_updated, error_message = order_service.update_order_with_items(order_id='order-1', data=data)

    check_conn = db_connection()
    saved_order = check_conn.execute(
        """
        SELECT
            customer_name, customer_email, customer_phone, customer_address, total, status
        FROM orders
        WHERE id = ?
        """,
        ('order-1',)
    ).fetchone()

    saved_items = check_conn.execute(
        """
        SELECT
            id, quantity
        FROM order_items
        WHERE order_id = ?
        ORDER BY id
        """,
        ('order-1',)
    ).fetchall()
    check_conn.close()

    assert is_updated is True
    assert error_message == ''

    assert saved_order['customer_name'] == 'Новое имя'
    assert saved_order['customer_email'] == 'new@mail.com'
    assert saved_order['customer_phone'] == '98765'
    assert saved_order['customer_address'] == 'new address'
    assert saved_order['total'] == 75000
    assert saved_order['status'] == 'new'

    assert saved_items[0]['id'] == first_item_id
    assert saved_items[0]['quantity'] == 2

    assert saved_items[1]['id'] == second_item_id
    assert saved_items[1]['quantity'] == 3


def test_update_order_with_items_rolls_back_when_item_is_not_found(empty_db, db_connection):
    conn = db_connection()

    create_test_product(
        conn=conn,
        product_id="product-1",
        name="Башня",
        price=30000,
    )

    create_test_order(
        conn=conn,
        order_id="order-1",
        customer_name="Старое имя",
        total=30000,
        status="new",
    )

    create_test_order_item(
        conn=conn,
        order_id="order-1",
        product_id="product-1",
        product_name="Башня",
        unit_price=30000,
        quantity=1,
    )

    conn.commit()

    saved_item = conn.execute(
        """
        SELECT id
        FROM order_items
        WHERE order_id = ?
        """,
        ("order-1",),
    ).fetchone()

    existing_item_id = saved_item["id"]

    conn.close()

    data = {
        "name": "Новое имя",
        "email": "new@email.com",
        "phone": "+79990000000",
        "address": "Новый адрес",
        "items": [
            {
                "id": existing_item_id,
                "quantity": 3,
            },
            {
                "id": 999999,
                "quantity": 2,
            },
        ],
        "total": 100000,
    }

    is_updated, error_message = (
        order_service.update_order_with_items(
            order_id="order-1",
            data=data,
        )
    )

    check_conn = db_connection()

    saved_order = check_conn.execute(
        """
        SELECT
            customer_name,
            total,
            status
        FROM orders
        WHERE id = ?
        """,
        ("order-1",),
    ).fetchone()

    saved_item = check_conn.execute(
        """
        SELECT quantity
        FROM order_items
        WHERE id = ?
        """,
        (existing_item_id,),
    ).fetchone()

    check_conn.close()

    assert is_updated is False
    assert error_message == "Одна из позиций заказа не найдена"

    assert saved_order["customer_name"] == "Старое имя"
    assert saved_order["total"] == 30000
    assert saved_order["status"] == "new"

    assert saved_item["quantity"] == 1
    
    
def test_create_order_with_items_reserves_all_products(empty_db, db_connection):
    conn = db_connection()
    create_test_product(
            conn=conn,
            product_id="product-1",
            name="Башня",
            price=30000
    )
    create_test_product(
            conn=conn,
            product_id="product-2",
            name="Чаша",
            price=5000
    )
    conn.commit()
    conn.close()
    
    items = [
        make_order_item("product-1", "Башня", 30000),
        make_order_item("product-2", "Чаша", 5000),
    ]
    
    is_created, error_message, order_id = order_service.create_order_with_items(
        data=make_checkout_data(),
        items=items
    )
    
    check_conn = db_connection()
    saved_products = check_conn.execute("SELECT id, status FROM products ORDER BY id").fetchall()
    check_conn.close()
    
    assert is_created is True
    assert error_message == ""
    assert order_id is not None
    
    assert saved_products[0]["id"] == "product-1"
    assert saved_products[0]["status"] == "reserved"
    
    assert saved_products[1]["id"] == "product-2"
    assert saved_products[1]["status"] == "reserved"
    
    
def test_create_order_with_items_rolls_back_when_product_cannot_be_reserved(empty_db, db_connection):
    conn = db_connection()
    create_test_product(
            conn=conn,
            product_id="product-1",
            name="Башня",
            price=30000,
            status="available"
    )
    create_test_product(
            conn=conn,
            product_id="product-2",
            name="Чаша",
            price=5000,
            status="reserved"
    )
    conn.commit()
    conn.close()
    
    items = [
        make_order_item("product-1", "Башня", 30000),
        make_order_item("product-2", "Чаша", 5000),
    ]
    
    is_created, error_message, order_id = order_service.create_order_with_items(
        data=make_checkout_data(),
        items=items
    )
    
    check_conn = db_connection()
    orders_count = check_conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    order_items_count = check_conn.execute("SELECT COUNT(*) FROM order_items").fetchone()[0]
    saved_products = check_conn.execute("SELECT id, status FROM products ORDER BY id").fetchall()
    check_conn.close()
    
    assert is_created is False
    assert error_message == "Работа «Чаша» больше недоступна"
    assert order_id is None
    
    assert orders_count == 0
    assert order_items_count == 0
    
    assert saved_products[0]["id"] == "product-1"
    assert saved_products[0]["status"] == "available"
    
    assert saved_products[1]["id"] == "product-2"
    assert saved_products[1]["status"] == "reserved"
    
    
def test_cancel_order_cancels_order_and_releases_product(empty_db, db_connection):
    conn = db_connection()
    create_test_order_with_item(
        conn=conn,
        order_status="new",
        product_status="reserved"
    )
    conn.commit()
    conn.close()
    
    is_canceled, error_message = order_service.cancel_order("order-1")
    
    check_conn = db_connection()
    saved_order = get_saved_order(check_conn)
    saved_product = get_saved_product(check_conn)
    saved_items_count = check_conn.execute("SELECT COUNT(*) FROM order_items WHERE order_id = ?", ("order-1",)).fetchone()[0]
    check_conn.close()
    
    assert is_canceled is True
    assert error_message == ""
    
    assert saved_order["status"] == "canceled"
    assert saved_product["status"] == "available"
    assert saved_items_count == 1
    
    
def test_cancel_order_does_not_cancel_completed_order(empty_db, db_connection):
    conn = db_connection()
    create_test_order_with_item(
        conn=conn,
        order_status="completed",
        product_status="sold"
    )
    conn.commit()
    conn.close()
    
    is_canceled, error_message = order_service.cancel_order("order-1")
    
    check_conn = db_connection()
    saved_order = get_saved_order(check_conn)
    saved_product = get_saved_product(check_conn)
    saved_items_count = check_conn.execute("SELECT COUNT(*) FROM order_items WHERE order_id = ?", ("order-1",)).fetchone()[0]
    check_conn.close()
    
    assert is_canceled is False
    assert error_message == "Заказ не найден или уже не может быть отменён"
    
    assert saved_order["status"] == "completed"
    assert saved_product["status"] == "sold"
    assert saved_items_count == 1
    
    
def test_cancel_order_rolls_back_when_product_cannot_be_released(empty_db, db_connection):
    conn = db_connection()
    
    create_test_product(conn=conn, status="reserved")
    create_test_product(
            conn=conn,
            product_id="product-2",
            name="Чаша",
            price=5000,
            status="available"
    )
    create_test_order(conn=conn)
    create_test_order_item(conn=conn)
    create_test_order_item(
            conn=conn,
            order_id="order-1",
            product_id="product-2",
            product_name="Чаша",
            unit_price=5000,
            quantity=1
    )
    
    conn.commit()
    conn.close()
    
    is_canceled, error_message = order_service.cancel_order("order-1")
    
    check_conn = db_connection()
    saved_order = get_saved_order(check_conn)
    first_saved_product = get_saved_product(check_conn, "product-1")
    second_saved_product = get_saved_product(check_conn, "product-2")
    saved_items_count = check_conn.execute("SELECT COUNT(*) FROM order_items WHERE order_id = ?", ("order-1",)).fetchone()[0]
    check_conn.close()
    
    assert is_canceled is False
    assert error_message == "Не удалось освободить работу «Чаша»"
    
    assert saved_order["status"] == "new"
    assert first_saved_product["status"] == "reserved"
    assert second_saved_product["status"] == "available"
    assert saved_items_count == 2


def test_delete_canceled_order_deletes_order_and_items_but_keeps_product(empty_db, db_connection):
    conn = db_connection()
    create_test_order_with_item(
        conn=conn,
        order_status="canceled",
        product_status="available"
    )
    conn.commit()
    conn.close()

    is_deleted, error_message = order_service.delete_canceled_order('order-1')

    check_conn = db_connection()
    orders_count = check_conn.execute("SELECT COUNT(*) FROM orders WHERE id = ?", ('order-1',)).fetchone()[0]
    order_items_count = check_conn.execute("SELECT COUNT(*) FROM order_items WHERE order_id = ?", ('order-1',)).fetchone()[0]
    saved_product = check_conn.execute("SELECT status FROM products WHERE id = ?", ('product-1',)).fetchone()
    check_conn.close()

    assert is_deleted is True
    assert error_message == ''

    assert orders_count == 0
    assert order_items_count == 0

    assert saved_product is not None
    assert saved_product['status'] == 'available'


def test_delete_canceled_order_does_not_delete_active_order(empty_db, db_connection):
    conn = db_connection()
    create_test_order_with_item(
        conn=conn,
        order_status="new",
        product_status="reserved"
    )
    conn.commit()
    conn.close()

    is_deleted, error_message = order_service.delete_canceled_order('order-1')

    check_conn = db_connection()
    saved_order = get_saved_order(check_conn)
    order_items_count = check_conn.execute("SELECT COUNT(*) FROM order_items WHERE order_id = ?", ('order-1',)).fetchone()[0]
    saved_product = get_saved_product(check_conn)
    check_conn.close()

    assert is_deleted is False
    assert error_message == "Удалить можно только отменённый заказ"

    assert saved_order is not None
    assert saved_order['status'] == 'new'

    assert order_items_count == 1

    assert saved_product is not None
    assert saved_product['status'] == 'reserved'


def test_confirm_order_transitions_new_to_confirmed(empty_db, db_connection):
    conn = db_connection()
    create_test_order_with_item(
        conn=conn,
        order_status="new",
        product_status="reserved"
    )
    conn.commit()
    conn.close()

    is_confirmed, error_message = order_service.confirm_order("order-1")

    check_conn = db_connection()
    saved_order = get_saved_order(check_conn)
    saved_product = get_saved_product(check_conn)
    check_conn.close()

    assert is_confirmed is True
    assert error_message == ""

    assert saved_order is not None
    assert saved_product is not None
    assert saved_order["status"] == "confirmed"
    assert saved_product["status"] == "reserved"


@pytest.mark.parametrize(
    ("order_status", "product_status"),
    [
        ("confirmed", "reserved"),
        ("completed", "sold"),
        ("canceled", "available"),
    ]
)
def test_confirm_order_leaves_non_new_order_unchanged(
        empty_db,
        db_connection,
        order_status,
        product_status
):
    conn = db_connection()
    create_test_order_with_item(
        conn=conn,
        order_status=order_status,
        product_status=product_status
    )
    conn.commit()
    conn.close()

    is_confirmed, error_message = order_service.confirm_order("order-1")

    check_conn = db_connection()
    saved_order = get_saved_order(check_conn)
    saved_product = get_saved_product(check_conn)
    check_conn.close()

    assert is_confirmed is False
    assert error_message == "Заказ не может быть подтверждён"

    assert saved_order is not None
    assert saved_product is not None
    assert saved_order["status"] == order_status
    assert saved_product["status"] == product_status


def test_complete_order_sets_order_to_completed_and_product_to_sold(empty_db, db_connection):
    conn = db_connection()
    create_test_order_with_item(
        conn=conn,
        order_status="confirmed",
        product_status="reserved"
    )
    conn.commit()
    conn.close()

    is_completed, error_message = order_service.complete_order("order-1")

    check_conn = db_connection()
    saved_order = get_saved_order(check_conn)
    saved_product = get_saved_product(check_conn)
    check_conn.close()

    assert is_completed is True
    assert error_message == ""

    assert saved_order is not None
    assert saved_product is not None
    assert saved_order["status"] == "completed"
    assert saved_product["status"] == "sold"


def test_complete_order_does_not_complete_new_order(empty_db, db_connection):
    conn = db_connection()
    create_test_order_with_item(
        conn=conn,
        order_status="new",
        product_status="reserved"
    )
    conn.commit()
    conn.close()

    is_completed, error_message = order_service.complete_order("order-1")

    check_conn = db_connection()
    saved_order = get_saved_order(check_conn)
    saved_product = get_saved_product(check_conn)
    check_conn.close()

    assert is_completed is False
    assert error_message == "Не удалось завершить заказ"

    assert saved_order is not None
    assert saved_product is not None
    assert saved_order["status"] == "new"
    assert saved_product["status"] == "reserved"


def test_complete_order_rolls_back_when_product_cannot_be_sold(empty_db, db_connection):
    conn = db_connection()

    create_test_product(
        conn=conn,
        product_id="product-1",
        name="Башня",
        price=30000,
        status="reserved"
    )
    create_test_product(
        conn=conn,
        product_id="product-2",
        name="Чаша",
        price=5000,
        status="available"
    )
    create_test_order(
        conn=conn,
        order_id="order-1",
        total=35000,
        status="confirmed"
    )
    create_test_order_item(
        conn=conn,
        order_id="order-1",
        product_id="product-1",
        product_name="Башня",
        unit_price=30000
    )
    create_test_order_item(
        conn=conn,
        order_id="order-1",
        product_id="product-2",
        product_name="Чаша",
        unit_price=5000
    )

    conn.commit()
    conn.close()

    is_completed, error_message = order_service.complete_order("order-1")

    check_conn = db_connection()
    saved_order = get_saved_order(check_conn)
    first_product = get_saved_product(check_conn, "product-1")
    second_product = get_saved_product(check_conn, "product-2")
    check_conn.close()

    assert is_completed is False
    assert error_message == "Не удалось изменить статус работы «Чаша»"

    assert saved_order is not None
    assert first_product is not None
    assert second_product is not None
    assert saved_order["status"] == "confirmed"
    assert first_product["status"] == "reserved"
    assert second_product["status"] == "available"


def test_update_order_with_items_does_not_update_confirmed_order(empty_db, db_connection):
    conn = db_connection()

    create_test_order_with_item(
        conn=conn,
        order_status="confirmed",
        product_status="reserved"
    )

    saved_item = conn.execute("SELECT id FROM order_items WHERE order_id = ?", ("order-1",)).fetchone()

    item_id = saved_item["id"]

    conn.commit()
    conn.close()

    data = {
        "name": "Новое имя",
        "email": "new@mail.com",
        "phone": "98765",
        "address": "Новый адрес",
        "items": [
            {
                "id": item_id,
                "quantity": 2
            }
        ],
        "total": 60000
    }

    is_updated, error_message = (
        order_service.update_order_with_items(
            order_id="order-1",
            data=data
        )
    )

    check_conn = db_connection()

    saved_order = get_saved_order(check_conn)

    saved_item = check_conn.execute("SELECT quantity FROM order_items WHERE id = ?", (item_id,)).fetchone()

    check_conn.close()

    assert is_updated is False
    assert error_message == (
        "Заказ не найден или уже нельзя редактировать"
    )

    assert saved_order is not None
    assert saved_item is not None

    assert saved_order["status"] == "confirmed"
    assert saved_order["customer_name"] == "Денис"
    assert saved_order["total"] == 30000
    assert saved_item["quantity"] == 1