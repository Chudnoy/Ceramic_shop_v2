import database.schema as schema


def test_init_db_runs_migrations_and_seeds_data(db_connection):
    schema.init_db()
    schema.init_db()

    conn = db_connection()

    saved_versions = conn.execute(
        """
        SELECT version
        FROM schema_migrations
        ORDER BY version
        """
    ).fetchall()

    category_count = conn.execute(
        "SELECT COUNT(*) AS count FROM categories"
    ).fetchone()["count"]

    tag_count = conn.execute("SELECT COUNT(*) AS count FROM tags").fetchone()["count"]

    product_count = conn.execute("SELECT COUNT(*) AS count FROM products").fetchone()[
        "count"
    ]

    conn.close()

    assert [row["version"] for row in saved_versions] == [1, 2, 3, 4, 5, 6, 7, 8]

    assert category_count == 5
    assert tag_count == 6
    assert product_count == 5
