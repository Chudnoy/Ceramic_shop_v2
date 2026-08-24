import pytest

import database.migrations as migrations
from database.migration_versions import v011_backfill_shop_core as v011


def prepare_v011(conn):
    migrations.run_migrations(conn, migrations.MIGRATIONS[:10])


def create_legacy_product(
    conn,
    product_id="product-1",
    name="Башня",
    price=30000,
    status="available",
    is_visible=1,
    is_for_sale=1,
    is_archived=0,
):
    conn.execute(
        """
        INSERT INTO products
            (id, name, price, status, is_visible, is_for_sale, is_archived)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (product_id, name, price, status, is_visible, is_for_sale, is_archived),
    )


def create_matching_work(conn, work_id="product-1", name="Башня"):
    conn.execute("INSERT INTO works (id, name) VALUES (?, ?)", (work_id, name))


def create_active_order_for_product(
    conn, product_id="product-1", order_id="order-1", status="new"
):
    conn.execute(
        """
        INSERT INTO orders
            (id, customer_name, customer_email, total, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order_id, "Покупатель", "buyer@gmail.com", 30000, status),
    )

    conn.execute(
        """
        INSERT INTO order_items
            (order_id, product_id, product_name, unit_price, quantity)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order_id, product_id, "Башня", 30000, 1),
    )


def test_v011_backfills_available_product_for_sale_as_unique_shop_item(db_connection):
    conn = db_connection()

    prepare_v011(conn)
    create_legacy_product(conn)
    create_matching_work(conn)

    v011.apply(conn)

    saved = conn.execute(
        """
        SELECT
            id,
            work_id,
            name,
            description,
            dimensions,
            sales_note,
            price,
            inventory_type,
            stock_quantity,
            is_published,
            is_orderable,
            is_retired
        FROM shop_items
        WHERE work_id = ?
        """,
        ("product-1",),
    ).fetchone()

    conn.close()

    assert saved is not None

    assert saved["id"] != "product-1"
    assert saved["work_id"] == "product-1"

    assert saved["name"] is None
    assert saved["description"] is None
    assert saved["dimensions"] is None
    assert saved["sales_note"] is None

    assert saved["price"] == 30000
    assert saved["inventory_type"] == "unique"
    assert saved["stock_quantity"] == 1

    assert saved["is_published"] == 1
    assert saved["is_orderable"] == 1
    assert saved["is_retired"] == 0


def test_v011_does_not_backfill_available_product_not_for_sale(db_connection):
    conn = db_connection()

    prepare_v011(conn)
    create_legacy_product(conn, is_for_sale=0)
    create_matching_work(conn)

    v011.apply(conn)

    saved = conn.execute(
        "SELECT id FROM shop_items WHERE work_id = ?", ("product-1",)
    ).fetchone()

    conn.close()

    assert saved is None


def test_v011_does_not_backfill_archived_available_product_for_sale(db_connection):
    conn = db_connection()

    prepare_v011(conn)
    create_legacy_product(conn, is_for_sale=1, is_archived=1)
    create_matching_work(conn)

    v011.apply(conn)

    saved = conn.execute(
        "SELECT id FROM shop_items WHERE work_id = ?", ("product-1",)
    ).fetchone()

    conn.close()

    assert saved is None


def test_v011_backfills_reserved_product_with_active_order(db_connection):
    conn = db_connection()

    prepare_v011(conn)
    create_legacy_product(
        conn, status="reserved", is_visible=1, is_for_sale=0, is_archived=0
    )
    create_matching_work(conn)
    create_active_order_for_product(conn)

    v011.apply(conn)

    saved = conn.execute(
        """
        SELECT
            work_id, price, inventory_type, stock_quantity, is_published, is_orderable, is_retired
        FROM shop_items
        WHERE work_id = ?
        """,
        ("product-1",),
    ).fetchone()

    conn.close()

    assert saved is not None

    assert saved["work_id"] == "product-1"
    assert saved["price"] == 30000
    assert saved["inventory_type"] == "unique"
    assert saved["stock_quantity"] == 1

    assert saved["is_published"] == 0
    assert saved["is_orderable"] == 0
    assert saved["is_retired"] == 0


def test_v011_does_not_backfill_sold_product(db_connection):
    conn = db_connection()

    prepare_v011(conn)
    create_legacy_product(
        conn, status="sold", is_visible=1, is_for_sale=1, is_archived=0
    )
    create_matching_work(conn)

    v011.apply(conn)

    saved = conn.execute(
        "SELECT id FROM shop_items WHERE work_id = ?", ("product-1",)
    ).fetchone()

    conn.close()

    assert saved is None


def test_v011_backfills_hidden_available_product_as_unpublished(db_connection):
    conn = db_connection()

    prepare_v011(conn)
    create_legacy_product(
        conn, status="available", is_visible=0, is_for_sale=1, is_archived=0
    )
    create_matching_work(conn)

    v011.apply(conn)

    saved = conn.execute(
        "SELECT is_published, is_orderable FROM shop_items WHERE work_id = ?",
        ("product-1",),
    ).fetchone()

    conn.close()

    assert saved is not None
    assert saved["is_published"] == 0
    assert saved["is_orderable"] == 1


def test_v011_rejects_nonempty_shop_backfill_target(db_connection):
    conn = db_connection()

    prepare_v011(conn)

    conn.execute(
        """
        INSERT INTO shop_items
            (id, name, price, inventory_type, stock_quantity)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("existing-shop-item", "Уже существующая позиция", 1000, "unique", 1),
    )

    with pytest.raises(
        ValueError, match="целевые таблицы Shop backfill уже содержат данные"
    ):
        v011.apply(conn)

    conn.close()


def test_v011_rejects_shop_product_without_matching_work(db_connection):
    conn = db_connection()

    prepare_v011(conn)
    create_legacy_product(conn, status="available", is_for_sale=1, is_archived=0)

    with pytest.raises(
        ValueError, match="найдены Shop products без соответствующей work"
    ):
        v011.apply(conn)

    conn.close()
