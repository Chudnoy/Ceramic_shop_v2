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