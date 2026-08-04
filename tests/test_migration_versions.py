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
        ('products',)
    ).fetchone()

    columns = conn.execute("PRAGMA table_info(products)").fetchall()

    column_names = {column['name'] for column in columns}

    saved_versions = conn.execute(
        """
        SELECT version, name
        FROM schema_migrations
        """
    ).fetchall()

    conn.close()

    assert saved_table is not None

    assert column_names == {'id', 'name', 'description', 'price', 'img'}
    assert any(column['name'] == 'id' and column['pk'] == 1 for column in columns)

    assert len(saved_versions) == 1
    assert saved_versions[0]['version'] == 1
    assert saved_versions[0]['name'] == 'create_products'


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

    assert category_column_names == { "id", "name", "slug", "description"}

    assert product_column_names == { "id", "name", "description", "price", "img", "category_id"}

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
    column_names = {column['name'] for column in columns}
    saved_versions = conn.execute("SELECT version, name FROM schema_migrations ORDER BY version").fetchall()

    conn.close()

    assert column_names == {'id', 'customer_name', 'customer_email', 'customer_phone', 'customer_address', 'items', 'total', 'created_at'}

    assert any(
        column['name'] == 'items'
        and column['type'] == 'TEXT'
        and column['notnull'] == 1
        for column in columns
    )

    assert 'status' not in column_names

    assert [row['version'] for row in saved_versions] == [1, 2, 3]

    assert [row['name'] for row in saved_versions] == [
        'create_products',
        'add_categories',
        'create_orders_with_json_items'
    ]


def test_v004_adds_checked_status_to_existing_order(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:3])

    conn.execute(
        """
        INSERT INTO orders (id, customer_name, customer_email, customer_phone, customer_address, items, total)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ('order-1', 'Денис', 'denis@example.com', None, None, '{}', 30000)
    )

    conn.commit()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:4])

    saved_order = conn.execute("SELECT status FROM orders WHERE id = ?", ('order-1',)).fetchone()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", ('banana', 'order-1'))

    conn.rollback()

    order_after_falled_update = conn.execute("SELECT status FROM orders WHERE id = ?", ('order-1',)).fetchone()

    saved_versions = conn.execute("SELECT version, name FROM schema_migrations ORDER BY version").fetchall()

    conn.close()

    assert saved_order['status'] == 'new'
    assert order_after_falled_update['status'] == 'new'

    assert [row['version'] for row in saved_versions] == [1, 2, 3, 4]
    assert saved_versions[-1]['name'] == 'add_order_status'


def test_v005_expands_existing_products_with_defaults_and_checks(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:4])

    conn.execute(
        """
        INSERT INTO products
        (id, name, description, price, img, category_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ('product-1', 'Башня', 'Интерьерный объект', 30000, 'tower.jpg', None)
    )

    conn.commit()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:5])

    columns = conn.execute("PRAGMA table_info(products)").fetchall()
    column_names = {column['name'] for column in columns}

    saved_product = conn.execute(
        """
        SELECT
            status, year, materials, is_visible, is_for_sale, is_archived, is_featured
        FROM products
        WHERE id = ?
        """,
        ('product-1',)
    ).fetchone()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE products SET status = ? WHERE id = ?", ('banana', 'product-1'))

    conn.rollback()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE products SET is_visible = ? WHERE id = ?", (2, 'product-1'))

    conn.rollback()

    product_after_faild_updates = conn.execute("SELECT status, is_visible FROM products WHERE id = ?", ('product-1',)).fetchone()

    saved_versions = conn.execute("SELECT version, name FROM schema_migrations ORDER BY version").fetchall()

    conn.close()

    assert column_names == {
        'id',
        'name',
        'description',
        'price',
        'img',
        'category_id',
        'status',
        'year',
        'materials',
        'is_visible',
        'is_for_sale',
        'is_archived',
        'is_featured'
    }

    assert saved_product['status'] == 'available'
    assert saved_product['year'] is None
    assert saved_product['materials'] == 'Каменная масса'
    assert saved_product['is_visible'] == 1
    assert saved_product['is_for_sale'] == 1
    assert saved_product['is_archived'] == 0
    assert saved_product['is_featured'] == 0

    assert product_after_faild_updates['status'] == 'available'
    assert product_after_faild_updates['is_visible'] == 1

    assert [row['version'] for row in saved_versions] == [1, 2, 3, 4, 5]

    assert saved_versions[-1]['name'] == 'expand_products'