import pytest

import database.migrations as migrations
import database.migration_versions.v009_backfill_artistic_core as v009


def create_legacy_product(
    conn,
    product_id="product-1",
    name="Работа 1",
    price=10000,
    materials="Каменная масса",
    status="available",
):
    conn.execute(
        "INSERT INTO products (id, name, price, materials, status) VALUES (?, ?, ?, ?, ?)",
        (product_id, name, price, materials, status),
    )


def create_legacy_order(conn, order_id="order-1", status="new"):
    conn.execute(
        """
        INSERT INTO orders
            (id, customer_name, customer_email, customer_phone, customer_address, total, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (order_id, "Покупатель", "buyer@example.com", "12345", "spb", 10000, status),
    )


def create_legacy_order_item(
    conn,
    order_id="order-1",
    product_id="product-1",
    product_name="Работа 1",
    quantity=1,
):
    conn.execute(
        """
        INSERT INTO order_items
            (order_id, product_id, product_name, unit_price, quantity)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order_id, product_id, product_name, 10000, quantity),
    )


def test_preflight_accepts_products_with_materials(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(conn=conn, materials="Каменная масса, глазурь")

    v009.preflight_products_have_materials(conn)

    conn.close()


@pytest.mark.parametrize("invalid_materials", ["", "     "])
def test_preflight_rejects_products_without_materials(db_connection, invalid_materials):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(conn=conn, materials=invalid_materials)

    with pytest.raises(ValueError):
        v009.preflight_products_have_materials(conn)

    conn.close()


def test_preflight_accepts_active_order_item_with_product(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(conn)
    create_legacy_order(conn)
    create_legacy_order_item(conn)

    v009.preflight_active_order_items_have_products(conn)

    conn.close()


@pytest.mark.parametrize("active_status", ["new", "confirmed"])
def test_preflight_rejects_active_order_item_without_product(
    db_connection, active_status
):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_order(conn=conn, status=active_status)
    create_legacy_order_item(conn=conn, product_id=None)

    with pytest.raises(ValueError):
        v009.preflight_active_order_items_have_products(conn)

    conn.close()


@pytest.mark.parametrize("historical_status", ["completed", "canceled"])
def test_preflight_accepts_historical_order_item_without_product(
    db_connection, historical_status
):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_order(conn=conn, status=historical_status)
    create_legacy_order_item(conn=conn, product_id=None)

    v009.preflight_active_order_items_have_products(conn)

    conn.close()


def test_preflight_accepts_consistent_product_statuses(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(conn=conn, product_id="available-product", status="available")
    create_legacy_product(conn=conn, product_id="reserved-product", status="reserved")
    create_legacy_product(conn=conn, product_id="sold-product", status="sold")
    create_legacy_order(conn=conn, order_id="active-order", status="new")
    create_legacy_order_item(
        conn=conn, order_id="active-order", product_id="reserved-product"
    )
    create_legacy_order(conn=conn, order_id="completed-order", status="completed")
    create_legacy_order_item(
        conn=conn, order_id="completed-order", product_id="sold-product"
    )

    v009.preflight_product_status_matches_active_orders(conn)

    conn.close()


@pytest.mark.parametrize("product_status", ["available", "sold"])
def test_preflight_rejects_non_reserved_product_in_active_order(
    db_connection, product_status
):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(conn, status=product_status)
    create_legacy_order(conn, status="new")
    create_legacy_order_item(conn)

    with pytest.raises(ValueError):
        v009.preflight_product_status_matches_active_orders(conn)

    conn.close()


def test_preflight_rejects_reserved_product_without_active_order(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(conn, status="reserved")

    with pytest.raises(ValueError):
        v009.preflight_product_status_matches_active_orders(conn)

    conn.close()


def test_preflight_rejects_reserved_product_with_multiple_active_units(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(conn, status="reserved")
    create_legacy_order(conn, status="new")
    create_legacy_order_item(conn, quantity=2)

    with pytest.raises(ValueError):
        v009.preflight_product_status_matches_active_orders(conn)

    conn.close()


def test_preflight_accepts_empty_backfill_targets(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    v009.preflight_backfill_targets_are_empty(conn)

    conn.close()


def test_preflight_rejects_nonempty_backfill_targets(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    conn.execute(
        "INSERT INTO materials (name, slug) VALUES (?, ?)", ("Глазурь", "glaze")
    )

    with pytest.raises(ValueError):
        v009.preflight_backfill_targets_are_empty(conn)

    conn.close()


def test_preflight_accepts_known_material_tokens(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(conn, materials=" Каменная масса, ГЛАЗУРЬ, фарфор ")

    v009.preflight_material_tokens_are_known(conn)

    conn.close()


def test_preflight_rejects_unknown_material_token(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(conn, materials="Каменная масса, золото")

    with pytest.raises(ValueError):
        v009.preflight_material_tokens_are_known(conn)

    conn.close()
