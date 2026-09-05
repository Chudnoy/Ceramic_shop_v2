import database.schema as schema


def test_init_db_runs_migrations_and_seeds_initial_data(db_connection):
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

    category_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]

    tag_count = conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0]

    material_count = conn.execute("SELECT COUNT(*) FROM materials").fetchone()[0]

    product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]

    works = conn.execute(
        """
        SELECT
            id,
            slug,
            name,
            is_published,
            is_commissionable
        FROM works
        ORDER BY name
        """
    ).fetchall()

    shop_items = conn.execute(
        """
        SELECT
            work_id,
            inventory_type,
            stock_quantity,
            is_published,
            is_orderable,
            is_retired
        FROM shop_items
        """
    ).fetchall()

    work_image_count = conn.execute("SELECT COUNT(*) FROM work_images").fetchone()[0]

    work_category_count = conn.execute(
        "SELECT COUNT(*) FROM work_categories"
    ).fetchone()[0]

    work_tag_count = conn.execute("SELECT COUNT(*) FROM work_tags").fetchone()[0]

    work_material_count = conn.execute(
        "SELECT COUNT(*) FROM work_materials"
    ).fetchone()[0]

    shop_states = conn.execute(
        """
        SELECT
            w.name,
            si.inventory_type,
            si.stock_quantity,
            si.is_published,
            si.is_orderable,
            si.is_retired
        FROM shop_items AS si
        JOIN works AS w
            ON w.id = si.work_id
        """
    ).fetchall()

    conn.close()

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
        13,
    ]

    assert category_count == 5
    assert tag_count == 6
    assert material_count == 3

    assert product_count == 0

    assert len(works) == 5
    assert len(shop_items) == 3

    assert work_image_count == 19
    assert work_category_count == 5
    assert work_tag_count == 7
    assert work_material_count == 11

    works_by_name = {work["name"]: work for work in works}

    assert set(works_by_name) == {
        "Капля",
        "Низкая чаша",
        "Колонна",
        "Белая чаша",
        "Кружка",
    }

    assert works_by_name["Капля"]["slug"] == "kaplya"
    assert works_by_name["Капля"]["is_published"] == 1

    assert works_by_name["Белая чаша"]["is_commissionable"] == 1
    assert works_by_name["Колонна"]["is_commissionable"] == 0

    shop_states_by_name = {row["name"]: row for row in shop_states}

    assert set(shop_states_by_name) == {
        "Капля",
        "Низкая чаша",
        "Кружка",
    }

    assert shop_states_by_name["Капля"]["inventory_type"] == "unique"
    assert shop_states_by_name["Капля"]["stock_quantity"] == 1
    assert shop_states_by_name["Капля"]["is_published"] == 1
    assert shop_states_by_name["Капля"]["is_orderable"] == 1
    assert shop_states_by_name["Капля"]["is_retired"] == 0

    assert shop_states_by_name["Низкая чаша"]["inventory_type"] == "unique"
    assert shop_states_by_name["Низкая чаша"]["stock_quantity"] == 1

    assert shop_states_by_name["Кружка"]["inventory_type"] == "stock"
    assert shop_states_by_name["Кружка"]["stock_quantity"] == 6
