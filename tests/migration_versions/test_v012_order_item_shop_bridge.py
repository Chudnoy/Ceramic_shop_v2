import database.migrations as migrations
from database.migration_versions import v012_add_shop_item_to_order_items as v012


def create_product(conn, product_id="product-1", name="Башня", price=30000):
    conn.execute(
        "INSERT INTO products (id, name, price) VALUES (?, ?, ?)",
        (product_id, name, price),
    )


def create_order(conn, order_id="order-1", status="new"):
    conn.execute(
        "INSERT INTO orders (id, customer_name, customer_email, total, status) VALUES (?, ?, ?, ?, ?)",
        (order_id, "Покупатель", "buyer@example.com", 30000, status),
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
        "INSERT INTO order_items (order_id, product_id, product_name, unit_price, quantity) VALUES (?, ?, ?, ?, ?)",
        (order_id, product_id, product_name, unit_price, quantity),
    )


def create_shop_item(
    conn,
    shop_item_id="shop-item-1",
    work_id=None,
    name="Тестовый товар",
    price=30000,
    inventory_type="unique",
    stock_quantity=1,
):
    conn.execute(
        """
        INSERT INTO shop_items
            (id, work_id, name, price, inventory_type, stock_quantity)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (shop_item_id, work_id, name, price, inventory_type, stock_quantity),
    )


def prepare_v012(conn):
    migrations.run_migrations(conn, migrations.MIGRATIONS[:11])
    v012.apply(conn)


def test_v012_adds_nullable_shop_item_id_to_order_items(db_connection):
    conn = db_connection()

    prepare_v012(conn)

    columns = conn.execute("PRAGMA table_info(order_items)").fetchall()

    column_by_name = {column["name"]: column for column in columns}

    conn.close()

    assert "shop_item_id" in column_by_name
    assert column_by_name["shop_item_id"]["notnull"] == 0


def test_v012_preserves_existing_order_item_and_adds_null_shop_item_id(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:11])

    create_product(conn)
    create_order(conn)
    create_legacy_order_item(conn)

    conn.commit()

    v012.apply(conn)

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

    assert saved["order_id"] == "order-1"
    assert saved["product_id"] == "product-1"
    assert saved["shop_item_id"] is None
    assert saved["product_name"] == "Башня"
    assert saved["unit_price"] == 30000
    assert saved["quantity"] == 1


def test_v012_shop_item_id_references_shop_items_with_set_null(db_connection):
    conn = db_connection()

    prepare_v012(conn)

    foreign_keys = conn.execute("PRAGMA foreign_key_list(order_items)").fetchall()

    conn.close()

    assert any(
        foreign_key["table"] == "shop_items"
        and foreign_key["from"] == "shop_item_id"
        and foreign_key["to"] == "id"
        and foreign_key["on_delete"] == "SET NULL"
        for foreign_key in foreign_keys
    )


def test_deleting_shop_item_preserves_order_item_and_clears_shop_item_id(db_connection):
    conn = db_connection()

    prepare_v012(conn)

    create_product(conn)
    create_order(conn)
    create_shop_item(conn)

    conn.execute(
        """
        INSERT INTO order_items
            (order_id, product_id, shop_item_id, product_name, unit_price, quantity)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("order-1", "product-1", "shop-item-1", "Башня", 30000, 1),
    )

    conn.commit()

    conn.execute("DELETE FROM shop_items WHERE id = ?", ("shop-item-1",))

    saved = conn.execute(
        """SELECT
            order_id, product_id, shop_item_id, product_name, unit_price, quantity
        FROM order_items
        WHERE order_id = ?
        """,
        ("order-1",),
    ).fetchone()

    conn.close()

    assert saved is not None

    assert saved["order_id"] == "order-1"
    assert saved["product_id"] == "product-1"
    assert saved["shop_item_id"] is None
    assert saved["product_name"] == "Башня"
    assert saved["unit_price"] == 30000
    assert saved["quantity"] == 1
