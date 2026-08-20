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

    product_ids = {
        row["id"] for row in conn.execute("SELECT id FROM products").fetchall()
    }
    work_ids = {row["id"] for row in conn.execute("SELECT id FROM works").fetchall()}
    work_image_count = conn.execute("SELECT COUNT(*) FROM work_images").fetchone()[0]
    work_category_count = conn.execute(
        "SELECT COUNT(*) FROM work_categories"
    ).fetchone()[0]
    work_material_count = conn.execute(
        "SELECT COUNT(*) FROM work_materials"
    ).fetchone()[0]

    tower = conn.execute("SELECT id FROM works WHERE name = ?", ("Башня",)).fetchone()

    tower_materials = conn.execute(
        """
        SELECT materials.name
        FROM work_materials
        JOIN materials
        ON materials.id = work_materials.material_id
        WHERE work_materials.work_id = ?
        ORDER BY materials.name
        """,
        (tower["id"],),
    ).fetchall()

    conn.close()

    assert [row["version"] for row in saved_versions] == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    assert category_count == 5
    assert tag_count == 6
    assert product_count == 5
    assert len(product_ids) == 5
    assert work_ids == product_ids
    assert work_image_count == 5
    assert work_category_count == 5
    assert work_material_count == 14

    assert [row["name"] for row in tower_materials] == [
        "Глазурь",
        "Каменная масса",
        "Фарфор",
    ]
