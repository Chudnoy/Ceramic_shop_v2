import sqlite3

import pytest

import database.migrations as migrations


def create_project(
    conn,
    project_id="project-1",
    name="Проект 1",
    slug="project-1",
):
    conn.execute(
        """
        INSERT INTO projects (
            id,
            name,
            slug
        )
        VALUES (?, ?, ?)
        """,
        (project_id, name, slug),
    )


def create_series(
    conn,
    series_id="series-1",
    name="Серия 1",
):
    conn.execute(
        """
        INSERT INTO series (
            id,
            name
        )
        VALUES (?, ?)
        """,
        (series_id, name),
    )


def create_work(
    conn,
    work_id="work-1",
    name="Работа 1",
    project_id=None,
    series_id=None,
    project_position=None,
):
    conn.execute(
        """
        INSERT INTO works (
            id,
            name,
            project_id,
            series_id,
            project_position
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            work_id,
            name,
            project_id,
            series_id,
            project_position,
        ),
    )


def create_category(conn, name="Скульптура", slug="sculpture"):
    cursor = conn.execute(
        "INSERT INTO categories (name, slug) VALUES (?, ?)", (name, slug)
    )
    return cursor.lastrowid


def create_tag(conn, name="Архитектура", slug="architecture"):
    cursor = conn.execute("INSERT INTO tags (name, slug) VALUES (?, ?)", (name, slug))
    return cursor.lastrowid


def create_material(conn, name="Каменная масса", slug="stoneware"):
    cursor = conn.execute(
        "INSERT INTO materials (name, slug) VALUES (?, ?)", (name, slug)
    )
    return cursor.lastrowid


def get_legacy_v007_snapshot(conn):
    return {
        "categories": [
            tuple(row)
            for row in conn.execute(
                "SELECT id, name, slug, description FROM categories ORDER BY id"
            ).fetchall()
        ],
        "tags": [
            tuple(row)
            for row in conn.execute(
                "SELECT id, name, slug FROM tags ORDER BY id"
            ).fetchall()
        ],
        "products": [
            tuple(row)
            for row in conn.execute(
                "SELECT id, name, description, price, img, category_id, status, year, materials, is_visible, is_for_sale, is_archived, is_featured FROM products ORDER BY id"
            ).fetchall()
        ],
        "product_tags": [
            tuple(row)
            for row in conn.execute(
                "SELECT product_id, tag_id FROM product_tags ORDER BY product_id, tag_id"
            ).fetchall()
        ],
        "orders": [
            tuple(row)
            for row in conn.execute(
                "SELECT id, customer_name, customer_email, customer_phone, customer_address, total, status, created_at FROM orders ORDER BY id"
            ).fetchall()
        ],
        "order_items": [
            tuple(row)
            for row in conn.execute(
                "SELECT  id, order_id, product_id, product_name, unit_price, quantity FROM order_items ORDER BY id"
            ).fetchall()
        ],
    }


def test_v008_preserves_existing_v007_data(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:7])

    category_cursor = conn.execute(
        """
        INSERT INTO categories (name, slug, description)
        VALUES (?, ?, ?)
        """,
        ("Скульптура", "sculpture", "Скульптурные объекты"),
    )

    category_id = category_cursor.lastrowid

    tag_cursor = conn.execute(
        """
        INSERT INTO tags (name, slug)
        VALUES (?, ?)
        """,
        ("Архитектура", "architecture"),
    )

    tag_id = tag_cursor.lastrowid

    conn.execute(
        """
        INSERT INTO products (
            id, 
            name,
            description,
            price,
            img,
            category_id,
            status,
            year,
            materials,
            is_visible,
            is_for_sale,
            is_archived,
            is_featured
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "product-1",
            "Башня",
            "Керамический объект",
            30000,
            "tower.jpg",
            category_id,
            "reserved",
            2024,
            "Каменная масса, глазурь",
            1,
            1,
            0,
            1,
        ),
    )

    conn.execute(
        """
        INSERT INTO product_tags (product_id, tag_id)
        VALUES (?, ?)
        """,
        ("product-1", tag_id),
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
            "confirmed",
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
        ("order-1", "product-1", "Башня", 30000, 1),
    )

    conn.commit()

    legacy_before = get_legacy_v007_snapshot(conn)

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    legacy_after = get_legacy_v007_snapshot(conn)

    new_tables = (
        "projects",
        "series",
        "materials",
        "works",
        "project_images",
        "work_images",
        "work_categories",
        "work_tags",
        "work_materials",
    )

    new_table_counts = {
        table_name: conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        for table_name in new_tables
    }

    saved_versions = [
        row["version"]
        for row in conn.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()
    ]

    conn.close()

    assert legacy_after == legacy_before

    assert new_table_counts == {
        "projects": 0,
        "series": 0,
        "materials": 0,
        "works": 0,
        "project_images": 0,
        "work_images": 0,
        "work_categories": 0,
        "work_tags": 0,
        "work_materials": 0,
    }

    assert saved_versions == [1, 2, 3, 4, 5, 6, 7, 8]


def test_work_cannot_belong_to_project_and_series(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_project(conn)
    create_series(conn)

    with pytest.raises(sqlite3.IntegrityError):
        create_work(conn, project_id="project-1", series_id="series-1")

    conn.rollback()
    conn.close()


def test_work_can_belong_to_project_or_series_or_neither(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_project(conn)
    create_series(conn)

    create_work(conn, work_id="work-project", project_id="project-1")
    create_work(conn, work_id="work-series", series_id="series-1")
    create_work(conn, work_id="work-independent")

    saved_works = conn.execute(
        "SELECT id, project_id, series_id FROM works ORDER BY id"
    ).fetchall()

    conn.close()

    saved_by_id = {row["id"]: row for row in saved_works}

    assert saved_by_id["work-project"]["project_id"] == "project-1"
    assert saved_by_id["work-project"]["series_id"] is None

    assert saved_by_id["work-series"]["project_id"] is None
    assert saved_by_id["work-series"]["series_id"] == "series-1"

    assert saved_by_id["work-independent"]["project_id"] is None
    assert saved_by_id["work-independent"]["series_id"] is None


def test_project_position_requires_project(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    with pytest.raises(sqlite3.IntegrityError):
        create_work(conn, project_position=1)

    conn.rollback()
    conn.close()


@pytest.mark.parametrize("invalid_position", [0, -5])
def test_project_position_must_be_positive(db_connection, invalid_position):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_project(conn)

    with pytest.raises(sqlite3.IntegrityError):
        create_work(conn, project_id="project-1", project_position=invalid_position)

    conn.rollback()
    conn.close()


def test_project_position_is_unique_within_project(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_project(conn=conn, project_id="project-1", name="Проект 1", slug="project-1")
    create_project(conn=conn, project_id="project-2", name="Проект 2", slug="project-2")
    create_work(
        conn=conn, work_id="work-project-1", project_id="project-1", project_position=1
    )
    create_work(
        conn=conn, work_id="work-project-2", project_id="project-2", project_position=1
    )

    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        create_work(
            conn=conn,
            work_id="duplicate_position",
            project_id="project-1",
            project_position=1,
        )

    conn.rollback()
    conn.close()


def test_deleting_work_cascades_owned_relations(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_work(conn)

    category_id = create_category(conn)
    tag_id = create_tag(conn)
    material_id = create_material(conn)

    conn.execute(
        "INSERT INTO work_images (work_id, image_path, position) VALUES (?, ?, ?)",
        ("work-1", "work-1.jpg", 1),
    )

    conn.execute(
        "INSERT INTO work_categories (work_id, category_id) VALUES (?, ?)",
        ("work-1", category_id),
    )

    conn.execute(
        "INSERT INTO work_tags (work_id, tag_id) VALUES (?, ?)", ("work-1", tag_id)
    )

    conn.execute(
        "INSERT INTO work_materials (work_id, material_id) VALUES (?, ?)",
        ("work-1", material_id),
    )

    conn.commit()

    conn.execute("DELETE FROM works WHERE id = ?", ("work-1",))

    conn.commit()

    work_images = conn.execute("SELECT * FROM work_images").fetchall()
    work_categories = conn.execute("SELECT * FROM work_categories").fetchall()
    work_tags = conn.execute("SELECT * FROM work_tags").fetchall()
    work_materials = conn.execute("SELECT * FROM work_materials").fetchall()

    categories = conn.execute("SELECT id FROM categories").fetchall()
    tags = conn.execute("SELECT id FROM tags").fetchall()
    materials = conn.execute("SELECT id FROM materials").fetchall()

    conn.close()

    assert work_categories == []
    assert work_images == []
    assert work_tags == []
    assert work_materials == []

    assert len(categories) == 1
    assert len(tags) == 1
    assert len(materials) == 1


def test_deleting_tag_cascades_work_tag_relation(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_work(conn)
    tag_id = create_tag(conn)

    conn.execute(
        "INSERT INTO work_tags (work_id, tag_id) VALUES (?, ?)", ("work-1", tag_id)
    )

    conn.commit()

    conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))

    conn.commit()

    saved_work = conn.execute(
        "SELECT id FROM works WHERE id = ?", ("work-1",)
    ).fetchone()
    saved_tag = conn.execute("SELECT id FROM tags WHERE id = ?", (tag_id,)).fetchone()
    saved_relation = conn.execute(
        "SELECT work_id, tag_id FROM work_tags WHERE work_id = ?", ("work-1",)
    ).fetchone()

    conn.close()

    assert saved_work is not None
    assert saved_tag is None
    assert saved_relation is None


@pytest.mark.parametrize(
    ("parent_table", "relation_table", "foreign_key_column", "create_parent"),
    [
        ("categories", "work_categories", "category_id", create_category),
        ("materials", "work_materials", "material_id", create_material),
    ],
)
def test_cannot_delete_category_or_material_used_by_work(
    db_connection, parent_table, relation_table, foreign_key_column, create_parent
):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_work(conn)
    parent_id = create_parent(conn)

    conn.execute(
        f"INSERT INTO {relation_table} (work_id, {foreign_key_column}) VALUES (?, ?)",
        ("work-1", parent_id),
    )

    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(f"DELETE FROM {parent_table} WHERE id = ?", (parent_id,))

    conn.rollback()

    saved_parent = conn.execute(
        f"SELECT id FROM {parent_table} WHERE id = ?", (parent_id,)
    ).fetchone()
    saved_relation = conn.execute(
        f"SELECT work_id FROM {relation_table} WHERE work_id = ? AND {foreign_key_column} = ?",
        ("work-1", parent_id),
    ).fetchone()

    conn.close()

    assert saved_parent is not None
    assert saved_relation is not None


def test_cannot_delete_project_used_by_work(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_project(conn)
    create_work(conn=conn, project_id="project-1")

    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM projects WHERE id = ?", ("project-1",))

    conn.rollback()

    saved_project = conn.execute(
        "SELECT id FROM projects WHERE id = ?", ("project-1",)
    ).fetchone()
    saved_work = conn.execute(
        "SELECT project_id FROM works WHERE id = ?", ("work-1",)
    ).fetchone()

    conn.close()

    assert saved_project is not None
    assert saved_work is not None
    assert saved_work["project_id"] == "project-1"


def test_cannot_delete_series_used_by_work(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_series(conn)
    create_work(conn=conn, series_id="series-1")

    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM series WHERE id = ?", ("series-1",))

    conn.rollback()

    saved_series = conn.execute(
        "SELECT id FROM series WHERE id = ?", ("series-1",)
    ).fetchone()
    saved_work = conn.execute(
        "SELECT series_id FROM works WHERE id = ?", ("work-1",)
    ).fetchone()

    conn.close()

    assert saved_series is not None
    assert saved_work is not None
    assert saved_work["series_id"] == "series-1"
