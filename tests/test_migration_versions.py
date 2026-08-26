import json
import sqlite3

import pytest

import database.migrations as migrations


def test_v001_creates_initial_products_table(db_connection):

    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:1])

    saved_table = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = ?
        """,
        ("products",),
    ).fetchone()

    columns = conn.execute("PRAGMA table_info(products)").fetchall()

    column_names = {column["name"] for column in columns}

    saved_versions = conn.execute(
        """
        SELECT version, name
        FROM schema_migrations
        """
    ).fetchall()

    conn.close()

    assert saved_table is not None

    assert column_names == {"id", "name", "description", "price", "img"}
    assert any(column["name"] == "id" and column["pk"] == 1 for column in columns)

    assert len(saved_versions) == 1
    assert saved_versions[0]["version"] == 1
    assert saved_versions[0]["name"] == "create_products"


def test_v002_adds_categories_and_product_relation(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:2])

    category_columns = conn.execute("PRAGMA table_info(categories)").fetchall()

    category_column_names = {column["name"] for column in category_columns}

    product_columns = conn.execute("PRAGMA table_info(products)").fetchall()

    product_column_names = {column["name"] for column in product_columns}

    foreign_keys = conn.execute("PRAGMA foreign_key_list(products)").fetchall()

    saved_versions = conn.execute(
        """
        SELECT version, name
        FROM schema_migrations
        ORDER BY version
        """
    ).fetchall()

    conn.close()

    assert category_column_names == {"id", "name", "slug", "description"}

    assert product_column_names == {
        "id",
        "name",
        "description",
        "price",
        "img",
        "category_id",
    }

    assert any(
        foreign_key["table"] == "categories"
        and foreign_key["from"] == "category_id"
        and foreign_key["to"] == "id"
        for foreign_key in foreign_keys
    )

    assert [row["version"] for row in saved_versions] == [1, 2]

    assert [row["name"] for row in saved_versions] == [
        "create_products",
        "add_categories",
    ]


def test_003_creates_order_with_json_items(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:3])

    columns = conn.execute("PRAGMA table_info(orders)").fetchall()
    column_names = {column["name"] for column in columns}
    saved_versions = conn.execute(
        "SELECT version, name FROM schema_migrations ORDER BY version"
    ).fetchall()

    conn.close()

    assert column_names == {
        "id",
        "customer_name",
        "customer_email",
        "customer_phone",
        "customer_address",
        "items",
        "total",
        "created_at",
    }

    assert any(
        column["name"] == "items"
        and column["type"] == "TEXT"
        and column["notnull"] == 1
        for column in columns
    )

    assert "status" not in column_names

    assert [row["version"] for row in saved_versions] == [1, 2, 3]

    assert [row["name"] for row in saved_versions] == [
        "create_products",
        "add_categories",
        "create_orders_with_json_items",
    ]


def test_v004_adds_checked_status_to_existing_order(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:3])

    conn.execute(
        """
        INSERT INTO orders (id, customer_name, customer_email, customer_phone, customer_address, items, total)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("order-1", "Денис", "denis@example.com", None, None, "{}", 30000),
    )

    conn.commit()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:4])

    saved_order = conn.execute(
        "SELECT status FROM orders WHERE id = ?", ("order-1",)
    ).fetchone()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", ("banana", "order-1"))

    conn.rollback()

    order_after_falled_update = conn.execute(
        "SELECT status FROM orders WHERE id = ?", ("order-1",)
    ).fetchone()

    saved_versions = conn.execute(
        "SELECT version, name FROM schema_migrations ORDER BY version"
    ).fetchall()

    conn.close()

    assert saved_order["status"] == "new"
    assert order_after_falled_update["status"] == "new"

    assert [row["version"] for row in saved_versions] == [1, 2, 3, 4]
    assert saved_versions[-1]["name"] == "add_order_status"


def test_v005_expands_existing_products_with_defaults_and_checks(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:4])

    conn.execute(
        """
        INSERT INTO products
        (id, name, description, price, img, category_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("product-1", "Башня", "Интерьерный объект", 30000, "tower.jpg", None),
    )

    conn.commit()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:5])

    columns = conn.execute("PRAGMA table_info(products)").fetchall()
    column_names = {column["name"] for column in columns}

    saved_product = conn.execute(
        """
        SELECT
            status, year, materials, is_visible, is_for_sale, is_archived, is_featured
        FROM products
        WHERE id = ?
        """,
        ("product-1",),
    ).fetchone()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "UPDATE products SET status = ? WHERE id = ?", ("banana", "product-1")
        )

    conn.rollback()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "UPDATE products SET is_visible = ? WHERE id = ?", (2, "product-1")
        )

    conn.rollback()

    product_after_faild_updates = conn.execute(
        "SELECT status, is_visible FROM products WHERE id = ?", ("product-1",)
    ).fetchone()

    saved_versions = conn.execute(
        "SELECT version, name FROM schema_migrations ORDER BY version"
    ).fetchall()

    conn.close()

    assert column_names == {
        "id",
        "name",
        "description",
        "price",
        "img",
        "category_id",
        "status",
        "year",
        "materials",
        "is_visible",
        "is_for_sale",
        "is_archived",
        "is_featured",
    }

    assert saved_product["status"] == "available"
    assert saved_product["year"] is None
    assert saved_product["materials"] == "Каменная масса"
    assert saved_product["is_visible"] == 1
    assert saved_product["is_for_sale"] == 1
    assert saved_product["is_archived"] == 0
    assert saved_product["is_featured"] == 0

    assert product_after_faild_updates["status"] == "available"
    assert product_after_faild_updates["is_visible"] == 1

    assert [row["version"] for row in saved_versions] == [1, 2, 3, 4, 5]

    assert saved_versions[-1]["name"] == "expand_products"


def test_v006_create_tags_and_product_tags_relations(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:6])

    tag_columns = conn.execute("PRAGMA table_info(tags)").fetchall()
    product_tags_columns = conn.execute("PRAGMA table_info(product_tags)").fetchall()
    foreign_keys = conn.execute("PRAGMA foreign_key_list(product_tags)").fetchall()

    conn.execute(
        """
        INSERT INTO products
            (id, name, price)
        VALUES (?, ?, ?)
        """,
        ("product-1", "Башня", 30000),
    )

    tag_cursor = conn.execute(
        """
        INSERT INTO tags (name, slug)
        VALUES (?, ?)
        """,
        ("Дом", "home"),
    )

    tag_id = tag_cursor.lastrowid

    conn.execute(
        """
        INSERT INTO product_tags
            (product_id, tag_id)
        VALUES (?, ?)
        """,
        ("product-1", tag_id),
    )

    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO product_tags
                (product_id, tag_id)
            VALUES (?, ?)
            """,
            ("product-1", tag_id),
        )

    conn.rollback()

    conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
    conn.commit()

    saved_links = conn.execute("SELECT product_id, tag_id FROM product_tags").fetchall()
    saved_versions = conn.execute(
        "SELECT version, name FROM schema_migrations ORDER BY version"
    ).fetchall()

    conn.close()

    assert {column["name"] for column in tag_columns} == {"id", "name", "slug"}
    assert {column["name"] for column in product_tags_columns} == {
        "product_id",
        "tag_id",
    }

    primary_key_columns = {
        column["name"]: column["pk"] for column in product_tags_columns
    }

    assert primary_key_columns == {"product_id": 1, "tag_id": 2}

    assert any(
        foreign_key["table"] == "products"
        and foreign_key["from"] == "product_id"
        and foreign_key["to"] == "id"
        and foreign_key["on_delete"] == "CASCADE"
        for foreign_key in foreign_keys
    )

    assert any(
        foreign_key["table"] == "tags"
        and foreign_key["from"] == "tag_id"
        and foreign_key["to"] == "id"
        and foreign_key["on_delete"] == "CASCADE"
        for foreign_key in foreign_keys
    )

    assert saved_links == []

    assert [row["version"] for row in saved_versions] == [1, 2, 3, 4, 5, 6]
    assert saved_versions[-1]["name"] == "add_tags"


def test_v007_normalizes_json_order_items_without_losing_data(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:6])

    conn.execute(
        """
        INSERT INTO products (
            id,
            name,
            description,
            price,
            img,
            category_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("product-1", "Башня", None, 30000, None, None),
    )

    legacy_items = {
        "product-1": {"name": "Башня", "price": 30000, "quantity": 1},
        "deleted-product": {"name": "Исчезнувшая чаша", "price": 5000, "quantity": 2},
    }

    conn.execute(
        """
        INSERT INTO orders (
            id,
            customer_name,
            customer_email,
            customer_phone,
            customer_address,
            items,
            total,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "order-1",
            "Денис",
            "denis@example.com",
            "12345",
            "spb",
            json.dumps(legacy_items, ensure_ascii=False),
            40000,
            "confirmed",
        ),
    )

    conn.commit()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:7])

    order_columns = conn.execute("PRAGMA table_info(orders)").fetchall()
    order_items_columns = conn.execute("PRAGMA table_info(order_items)").fetchall()

    saved_order = conn.execute(
        """
        SELECT
            id,
            customer_name,
            customer_email,
            customer_phone,
            customer_address,
            total,
            status
        FROM orders WHERE id = ?
        """,
        ("order-1",),
    ).fetchone()

    saved_items = conn.execute(
        """
        SELECT
            order_id,
            product_id,
            product_name,
            unit_price,
            quantity
        FROM order_items WHERE order_id = ?
        """,
        ("order-1",),
    ).fetchall()

    saved_versions = conn.execute(
        "SELECT version, name FROM schema_migrations ORDER BY version"
    ).fetchall()

    saved_items_by_name = {item["product_name"]: item for item in saved_items}

    existing_product_item = saved_items_by_name["Башня"]
    deleted_product_item = saved_items_by_name["Исчезнувшая чаша"]

    conn.execute("DELETE FROM products WHERE id = ?", ("product-1",))

    conn.commit()

    item_after_product_deletion = conn.execute(
        """
        SELECT
            product_id,
            product_name,
            unit_price,
            quantity
        FROM order_items
        WHERE order_id = ? AND product_name = ?
        """,
        ("order-1", "Башня"),
    ).fetchone()

    conn.execute("DELETE FROM orders WHERE id = ?", ("order-1",))

    conn.commit()

    remaining_order_items = conn.execute("SELECT id FROM order_items").fetchall()

    conn.close()

    assert {column["name"] for column in order_columns} == {
        "id",
        "customer_name",
        "customer_email",
        "customer_phone",
        "customer_address",
        "total",
        "status",
        "created_at",
    }

    assert "items" not in {column["name"] for column in order_columns}

    assert {column["name"] for column in order_items_columns} == {
        "id",
        "order_id",
        "product_id",
        "product_name",
        "unit_price",
        "quantity",
    }

    assert saved_order["id"] == "order-1"
    assert saved_order["customer_name"] == "Денис"
    assert saved_order["customer_email"] == "denis@example.com"
    assert saved_order["customer_phone"] == "12345"
    assert saved_order["customer_address"] == "spb"
    assert saved_order["total"] == 40000
    assert saved_order["status"] == "confirmed"

    assert len(saved_items) == 2

    assert existing_product_item["order_id"] == "order-1"
    assert existing_product_item["product_id"] == "product-1"
    assert existing_product_item["unit_price"] == 30000
    assert existing_product_item["quantity"] == 1

    assert deleted_product_item["order_id"] == "order-1"
    assert deleted_product_item["product_id"] is None
    assert deleted_product_item["unit_price"] == 5000
    assert deleted_product_item["quantity"] == 2

    assert item_after_product_deletion["product_id"] is None
    assert item_after_product_deletion["product_name"] == "Башня"
    assert item_after_product_deletion["unit_price"] == 30000
    assert item_after_product_deletion["quantity"] == 1

    assert remaining_order_items == []

    assert [row["version"] for row in saved_versions] == [1, 2, 3, 4, 5, 6, 7]

    assert saved_versions[-1]["name"] == "normalize_order_items"


def test_v008_creates_artistic_core(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    table_names = {
        row["name"]
        for row in conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()
    }

    work_columns = conn.execute("PRAGMA table_info(works)").fetchall()

    work_foreign_keys = conn.execute("PRAGMA foreign_key_list(works)").fetchall()

    saved_versions = conn.execute(
        """
        SELECT version, name
        FROM schema_migrations
        ORDER BY version
        """
    ).fetchall()

    conn.close()

    new_tables = {
        "projects",
        "series",
        "materials",
        "works",
        "project_images",
        "work_images",
        "work_categories",
        "work_tags",
        "work_materials",
    }

    assert new_tables <= table_names

    assert {column["name"] for column in work_columns} == {
        "id",
        "slug",
        "name",
        "description",
        "year",
        "dimensions",
        "project_id",
        "series_id",
        "project_position",
        "is_published",
        "is_commissionable",
        "commission_note",
    }

    assert any(
        foreign_key["table"] == "projects"
        and foreign_key["from"] == "project_id"
        and foreign_key["to"] == "id"
        for foreign_key in work_foreign_keys
    )

    assert any(
        foreign_key["table"] == "series"
        and foreign_key["from"] == "series_id"
        and foreign_key["to"] == "id"
        for foreign_key in work_foreign_keys
    )

    assert [row["version"] for row in saved_versions] == [1, 2, 3, 4, 5, 6, 7, 8]

    assert saved_versions[-1]["name"] == "create_artistic_core"


def test_v009_backfills_artistic_core(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    conn.execute(
        """
        INSERT INTO products (
            id,
            name,
            price,
            materials,
            status
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "product-1",
            "Башня",
            30000,
            "Каменная масса, глазурь",
            "reserved",
        ),
    )

    conn.execute(
        """
        INSERT INTO orders (
            id,
            customer_name,
            customer_email,
            customer_phone,
            customer_address,
            total,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "order-1",
            "Покупатель",
            "buyer@example.com",
            "12345",
            "spb",
            30000,
            "new",
        ),
    )

    conn.execute(
        """
        INSERT INTO order_items (
            order_id,
            product_id,
            product_name,
            unit_price,
            quantity
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "order-1",
            "product-1",
            "Башня",
            30000,
            1,
        ),
    )

    conn.commit()

    migrations.run_migrations(conn, migrations.MIGRATIONS)

    saved_work = conn.execute(
        """
        SELECT id, name
        FROM works
        WHERE id = ?
        """,
        ("product-1",),
    ).fetchone()

    saved_order_item = conn.execute(
        """
        SELECT
            order_id,
            product_id,
            product_name,
            unit_price,
            quantity
        FROM order_items
        WHERE order_id = ?
        """,
        ("order-1",),
    ).fetchone()

    saved_versions = conn.execute(
        """
        SELECT version, name
        FROM schema_migrations
        ORDER BY version
        """
    ).fetchall()

    saved_migrations = {row["version"]: row["name"] for row in saved_versions}

    conn.close()

    assert saved_work["id"] == "product-1"
    assert saved_work["name"] == "Башня"

    assert saved_order_item["order_id"] == "order-1"
    assert saved_order_item["product_id"] == "product-1"
    assert saved_order_item["product_name"] == "Башня"
    assert saved_order_item["unit_price"] == 30000
    assert saved_order_item["quantity"] == 1

    assert [row["version"] for row in saved_versions] == [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
    ]
    assert saved_migrations[9] == "backfill_artistic_core"


def test_v011_upgrades_existing_v010_database_with_shop_backfill(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    conn.execute(
        "INSERT INTO products (id, name, price) VALUES (?, ?, ?)",
        ("product-1", "Башня", 30000),
    )

    conn.commit()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:10])

    work_before_upgrade = conn.execute(
        "SELECT id FROM works WHERE id = ?", ("product-1",)
    ).fetchone()
    shop_item_before_upgrade = conn.execute(
        "SELECT id FROM shop_items WHERE work_id = ?", ("product-1",)
    ).fetchone()

    migrations.run_migrations(conn, migrations.MIGRATIONS)

    shop_item_after_upgrade = conn.execute(
        """
        SELECT
            work_id, price, inventory_type, stock_quantity, is_published, is_orderable, is_retired
        FROM shop_items
        WHERE work_id = ?
        """,
        ("product-1",),
    ).fetchone()

    saved_versions = conn.execute(
        "SELECT version, name FROM schema_migrations ORDER BY version"
    ).fetchall()

    saved_migrations = {row["version"]: row["name"] for row in saved_versions}

    conn.close()

    assert work_before_upgrade is not None
    assert shop_item_before_upgrade is None

    assert shop_item_after_upgrade is not None
    assert shop_item_after_upgrade["work_id"] == "product-1"
    assert shop_item_after_upgrade["price"] == 30000
    assert shop_item_after_upgrade["inventory_type"] == "unique"
    assert shop_item_after_upgrade["stock_quantity"] == 1
    assert shop_item_after_upgrade["is_published"] == 1
    assert shop_item_after_upgrade["is_orderable"] == 1
    assert shop_item_after_upgrade["is_retired"] == 0

    assert [row["version"] for row in saved_versions] == [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
    ]
    assert saved_migrations[11] == "backfill_shop_core"


def test_v012_upgrades_existing_v011_database_with_order_item_shop_bridge(
    db_connection,
):
    conn = db_connection()

    migrations.run_migrations(
        conn,
        migrations.MIGRATIONS[:11],
    )

    conn.execute(
        """
        INSERT INTO products
            (id, name, price)
        VALUES (?, ?, ?)
        """,
        ("product-1", "Башня", 30000),
    )

    conn.execute(
        """
        INSERT INTO orders
            (id, customer_name, customer_email, total, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "order-1",
            "Покупатель",
            "buyer@example.com",
            30000,
            "new",
        ),
    )

    conn.execute(
        """
        INSERT INTO order_items
            (
                order_id,
                product_id,
                product_name,
                unit_price,
                quantity
            )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "order-1",
            "product-1",
            "Башня",
            30000,
            1,
        ),
    )

    conn.commit()

    migrations.run_migrations(
        conn,
        migrations.MIGRATIONS,
    )

    saved_item = conn.execute(
        """
        SELECT
            product_id,
            shop_item_id,
            product_name,
            unit_price,
            quantity
        FROM order_items
        WHERE order_id = ?
        """,
        ("order-1",),
    ).fetchone()

    saved_versions = conn.execute(
        """
        SELECT version, name
        FROM schema_migrations
        ORDER BY version
        """
    ).fetchall()

    saved_migrations = {row["version"]: row["name"] for row in saved_versions}

    conn.close()

    assert saved_item["product_id"] == "product-1"
    assert saved_item["shop_item_id"] is None
    assert saved_item["product_name"] == "Башня"
    assert saved_item["unit_price"] == 30000
    assert saved_item["quantity"] == 1

    assert [row["version"] for row in saved_versions] == [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
    ]

    assert saved_migrations[12] == "add_shop_item_to_order_items"
