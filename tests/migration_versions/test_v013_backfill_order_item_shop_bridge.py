import pytest

import database.migrations as migrations
from database.migration_versions import v013_backfill_order_item_shop_bridge as v013


def prepare_v013(conn):
    migrations.run_migrations(conn, migrations.MIGRATIONS[:12])


def create_legacy_product(
    conn, product_id="product-1", name="Башня", price=30000, status="reserved"
):
    conn.execute(
        """
        INSERT INTO products
            (id, name, price, status)
        VALUES (?, ?, ?, ?)
        """,
        (product_id, name, price, status),
    )


def create_matching_work(conn, work_id="product-1", name="Башня"):
    conn.execute("INSERT INTO works (id, name) VALUES (?, ?)", (work_id, name))


def create_order(
    conn,
    order_id="order-1",
    status="new",
    total=30000,
):
    conn.execute(
        """
        INSERT INTO orders
            (id, customer_name, customer_email, total, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order_id, "Покупатель", "buyer@example.com", total, status),
    )


def create_legacy_order_item(
    conn,
    order_id="order-1",
    product_id="product-1",
    product_name="Башня",
    unit_price=30000,
    quantity=1,
):
    conn.execute(
        """
        INSERT INTO order_items
            (order_id, product_id, product_name, unit_price, quantity)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order_id, product_id, product_name, unit_price, quantity),
    )


def create_order_with_legacy_item(
    conn,
    product_id="product-1",
    order_id="order-1",
    status="new",
):
    create_order(
        conn,
        order_id=order_id,
        status=status,
    )

    create_legacy_order_item(
        conn,
        order_id=order_id,
        product_id=product_id,
    )


def create_matching_shop_item(
    conn, shop_item_id="shop-item-1", work_id="product-1", price=30000
):
    conn.execute(
        """
        INSERT INTO shop_items
            (id, work_id, price, inventory_type, stock_quantity)
        VALUES (?, ?, ?, ?, ?)
        """,
        (shop_item_id, work_id, price, "unique", 1),
    )


def test_v013_rejects_active_order_item_without_matching_shop_item(db_connection):
    conn = db_connection()

    prepare_v013(conn)

    create_legacy_product(conn)
    create_matching_work(conn)
    create_order_with_legacy_item(conn)

    with pytest.raises(
        ValueError, match="активные позиции заказов без соответствующего ShopItem"
    ):
        v013.apply(conn)

    conn.close()


def test_v013_backfills_shop_item_id_for_active_order_item(db_connection):
    conn = db_connection()

    prepare_v013(conn)

    create_legacy_product(conn)
    create_matching_work(conn)
    create_order_with_legacy_item(conn)
    create_matching_shop_item(conn)

    v013.apply(conn)

    saved = conn.execute(
        """
        SELECT
            order_id, product_id, shop_item_id, product_name, unit_price, quantity
        FROM order_items
        WHERE order_id = ?
        """,
        ("order-1",),
    ).fetchone()

    conn.close()

    assert saved["product_id"] == "product-1"
    assert saved["shop_item_id"] == "shop-item-1"

    assert saved["product_name"] == "Башня"
    assert saved["unit_price"] == 30000
    assert saved["quantity"] == 1


def test_v013_does_not_backfill_completed_order_item(db_connection):
    conn = db_connection()

    prepare_v013(conn)

    create_legacy_product(conn, status="sold")
    create_matching_work(conn)
    create_order_with_legacy_item(conn, status="completed")
    create_matching_shop_item(conn)

    v013.apply(conn)

    saved = conn.execute(
        """
        SELECT
            order_id, product_id, shop_item_id, product_name, unit_price, quantity
        FROM order_items
        WHERE order_id = ?
        """,
        ("order-1",),
    ).fetchone()

    conn.close()

    assert saved["product_id"] == "product-1"
    assert saved["shop_item_id"] is None

    assert saved["product_name"] == "Башня"
    assert saved["unit_price"] == 30000
    assert saved["quantity"] == 1


def test_v013_backfills_correct_shop_item_id_for_each_active_order_item(db_connection):
    conn = db_connection()

    prepare_v013(conn)

    create_legacy_product(conn, product_id="product-1", name="Башня", price=30000)
    create_legacy_product(conn, product_id="product-2", name="Чаша", price=20000)
    create_matching_work(conn, work_id="product-1", name="Башня")
    create_matching_work(conn, work_id="product-2", name="Чаша")
    create_matching_shop_item(
        conn, shop_item_id="shop-item-1", work_id="product-1", price=30000
    )
    create_matching_shop_item(
        conn, shop_item_id="shop-item-2", work_id="product-2", price=20000
    )
    create_order(conn, order_id="order-1", status="new")
    create_legacy_order_item(
        conn,
        order_id="order-1",
        product_id="product-1",
        product_name="Башня",
        unit_price=30000,
    )
    create_legacy_order_item(
        conn,
        order_id="order-1",
        product_id="product-2",
        product_name="Чаша",
        unit_price=20000,
    )

    v013.apply(conn)

    saved = conn.execute(
        """
        SELECT product_id, shop_item_id
        FROM order_items
        WHERE order_id = ?
        ORDER BY product_id
        """,
        ("order-1",),
    ).fetchall()

    conn.close()

    assert len(saved) == 2

    assert saved[0]["product_id"] == "product-1"
    assert saved[0]["shop_item_id"] == "shop-item-1"

    assert saved[1]["product_id"] == "product-2"
    assert saved[1]["shop_item_id"] == "shop-item-2"


def test_v013_rejects_active_order_item_without_product_id(db_connection):
    conn = db_connection()

    prepare_v013(conn)

    create_order(
        conn,
        order_id="order-1",
        status="new",
    )

    create_legacy_order_item(
        conn,
        order_id="order-1",
        product_id=None,
        product_name="Башня",
        unit_price=30000,
    )

    with pytest.raises(
        ValueError,
        match="активные позиции заказов без соответствующего ShopItem",
    ):
        v013.apply(conn)

    conn.close()


def test_v013_rejects_nonempty_shop_item_bridge(db_connection):
    conn = db_connection()

    prepare_v013(conn)

    create_legacy_product(conn)
    create_matching_work(conn)
    create_matching_shop_item(conn)

    create_order_with_legacy_item(conn)

    conn.execute(
        """
        UPDATE order_items
        SET shop_item_id = ?
        WHERE order_id = ?
        """,
        ("shop-item-1", "order-1"),
    )

    with pytest.raises(
        ValueError,
        match="order_items.shop_item_id уже содержит данные",
    ):
        v013.apply(conn)

    conn.close()
