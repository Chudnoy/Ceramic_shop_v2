from database import shop_items
from services.shop_availability_service import get_shop_item_availability


def create_test_shop_item(
    conn,
    shop_item_id="shop-1",
    inventory_type="stock",
    stock_quantity=6,
    is_published=1,
    is_orderable=1,
    is_retired=0,
):
    conn.execute(
        """
        INSERT INTO shop_items (
            id,
            name,
            price,
            inventory_type,
            stock_quantity,
            is_published,
            is_orderable,
            is_retired
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            shop_item_id,
            "Кружка",
            5000,
            inventory_type,
            stock_quantity,
            is_published,
            is_orderable,
            is_retired,
        ),
    )


def create_test_order(
    conn,
    order_id="order-1",
    status="new",
):
    conn.execute(
        """
        INSERT INTO orders (
            id,
            customer_name,
            customer_email,
            total,
            status
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            order_id,
            "Денис",
            "denis@example.com",
            10000,
            status,
        ),
    )


def create_test_order_item(
    conn,
    order_id="order-1",
    shop_item_id="shop-1",
    quantity=1,
):
    conn.execute(
        """
        INSERT INTO order_items (
            order_id,
            shop_item_id,
            product_name,
            unit_price,
            quantity
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            order_id,
            shop_item_id,
            "Кружка",
            5000,
            quantity,
        ),
    )


def test_get_shop_item_availability_subtracts_reserved_quantity(
    empty_db,
    db_connection,
):
    conn = db_connection()

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        inventory_type="stock",
        stock_quantity=6,
    )

    create_test_order(
        conn,
        order_id="order-1",
        status="new",
    )

    create_test_order_item(
        conn,
        order_id="order-1",
        shop_item_id="shop-1",
        quantity=2,
    )

    shop_item = shop_items.get_shop_item_by_id(
        conn,
        "shop-1",
    )

    availability = get_shop_item_availability(
        conn,
        shop_item,
    )

    conn.close()

    assert availability == {
        "reserved_quantity": 2,
        "available_quantity": 4,
        "can_order": True,
    }


def test_get_shop_item_availability_returns_full_stock_without_reservations(
    empty_db,
    db_connection,
):
    conn = db_connection()

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        inventory_type="unique",
        stock_quantity=1,
    )

    shop_item = shop_items.get_shop_item_by_id(
        conn,
        "shop-1",
    )

    availability = get_shop_item_availability(
        conn,
        shop_item,
    )

    conn.close()

    assert availability == {
        "reserved_quantity": 0,
        "available_quantity": 1,
        "can_order": True,
    }


def test_get_shop_item_availability_can_order_available_item(
    empty_db,
    db_connection,
):
    conn = db_connection()

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        stock_quantity=3,
        is_published=1,
        is_orderable=1,
        is_retired=0,
    )

    shop_item = shop_items.get_shop_item_by_id(
        conn,
        "shop-1",
    )

    availability = get_shop_item_availability(
        conn,
        shop_item,
    )

    conn.close()

    assert availability["can_order"] is True


def test_get_shop_item_availability_cannot_order_when_ordering_disabled(
    empty_db,
    db_connection,
):
    conn = db_connection()

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        stock_quantity=3,
        is_published=1,
        is_orderable=0,
        is_retired=0,
    )

    shop_item = shop_items.get_shop_item_by_id(
        conn,
        "shop-1",
    )

    availability = get_shop_item_availability(
        conn,
        shop_item,
    )

    conn.close()

    assert availability["can_order"] is False


def test_get_shop_item_availability_cannot_order_retired_item(
    empty_db,
    db_connection,
):
    conn = db_connection()

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        stock_quantity=3,
        is_published=1,
        is_orderable=1,
        is_retired=1,
    )

    shop_item = shop_items.get_shop_item_by_id(
        conn,
        "shop-1",
    )

    availability = get_shop_item_availability(
        conn,
        shop_item,
    )

    conn.close()

    assert availability["can_order"] is False


def test_get_shop_item_availability_cannot_order_without_available_stock(
    empty_db,
    db_connection,
):
    conn = db_connection()

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        stock_quantity=2,
        is_published=1,
        is_orderable=1,
        is_retired=0,
    )

    create_test_order(
        conn,
        order_id="order-1",
        status="new",
    )

    create_test_order_item(
        conn,
        order_id="order-1",
        shop_item_id="shop-1",
        quantity=2,
    )

    shop_item = shop_items.get_shop_item_by_id(
        conn,
        "shop-1",
    )

    availability = get_shop_item_availability(
        conn,
        shop_item,
    )

    conn.close()

    assert availability["available_quantity"] == 0
    assert availability["can_order"] is False


def test_get_shop_item_availability_cannot_order_unpublished_item(
    empty_db,
    db_connection,
):
    conn = db_connection()

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        stock_quantity=3,
        is_published=0,
        is_orderable=1,
        is_retired=0,
    )

    shop_item = shop_items.get_shop_item_by_id(
        conn,
        "shop-1",
    )

    availability = get_shop_item_availability(
        conn,
        shop_item,
    )

    conn.close()

    assert availability["can_order"] is False
