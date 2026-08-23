import sqlite3

import pytest

import database.migrations as migrations
from database.migration_versions import v010_create_shop_core as v010


def prepare_v010(conn):
    migrations.run_migrations(conn, migrations.MIGRATIONS[:9])
    v010.apply(conn)


def create_work(conn, work_id="work-1", name="Работа 1"):
    conn.execute("INSERT INTO works (id, name) VALUES (?, ?)", (work_id, name))


def create_shop_item(
    conn,
    shop_item_id="shop-item-1",
    work_id=None,
    name="Тестовый товар",
    description=None,
    dimensions=None,
    price=1000,
    inventory_type="stock",
    stock_quantity=1,
):
    conn.execute(
        """
        INSERT INTO shop_items
            (id, work_id, name, description, dimensions, price, inventory_type, stock_quantity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            shop_item_id,
            work_id,
            name,
            description,
            dimensions,
            price,
            inventory_type,
            stock_quantity,
        ),
    )


def create_shop_item_image(
    conn, shop_item_id="shop-item-1", image_path="test-image.jpg", position=1
):
    conn.execute(
        """
        INSERT INTO shop_item_images
            (shop_item_id, image_path, position)
        VALUES (?, ?, ?)
        """,
        (shop_item_id, image_path, position),
    )


def create_category(conn, name="Категория 1", slug="category-1"):
    cursor = conn.execute(
        "INSERT INTO categories (name, slug) VALUES (?, ?)", (name, slug)
    )

    return cursor.lastrowid


def create_tag(conn, name="Тег 1", slug="tag-1"):
    cursor = conn.execute("INSERT INTO tags (name, slug) VALUES (?, ?)", (name, slug))

    return cursor.lastrowid


def create_material(conn, name="Материал 1", slug="material-1"):
    cursor = conn.execute(
        "INSERT INTO materials (name, slug) VALUES (?, ?)", (name, slug)
    )

    return cursor.lastrowid


def link_shop_item_to_category(conn, shop_item_id, category_id):
    conn.execute(
        """
        INSERT INTO shop_item_categories
            (shop_item_id, category_id)
        VALUES (?, ?)
        """,
        (shop_item_id, category_id),
    )


def link_shop_item_to_tag(conn, shop_item_id, tag_id):
    conn.execute(
        """
        INSERT INTO shop_item_tags
            (shop_item_id, tag_id)
        VALUES (?, ?)
        """,
        (shop_item_id, tag_id),
    )


def link_shop_item_to_material(conn, shop_item_id, material_id):
    conn.execute(
        """
        INSERT INTO shop_item_materials
            (shop_item_id, material_id)
        VALUES (?, ?)
        """,
        (shop_item_id, material_id),
    )


SHOP_TABLES = {
    "shop_items",
    "shop_item_images",
    "shop_item_categories",
    "shop_item_tags",
    "shop_item_materials",
}


def test_v010_creates_empty_shop_core_tables(db_connection):
    conn = db_connection()

    prepare_v010(conn)

    existing_shop_tables = {
        row["name"]
        for row in conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()
        if row["name"] in SHOP_TABLES
    }

    shop_table_counts = {
        table_name: conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        for table_name in existing_shop_tables
    }

    conn.close()

    assert existing_shop_tables == SHOP_TABLES
    assert shop_table_counts == {table_name: 0 for table_name in SHOP_TABLES}


def test_linked_shop_item_can_inherit_content_from_work(db_connection):
    conn = db_connection()

    prepare_v010(conn)
    create_work(conn)

    create_shop_item(
        conn,
        work_id="work-1",
        name=None,
        price=30000,
        inventory_type="unique",
        stock_quantity=1,
    )

    saved = conn.execute(
        "SELECT work_id, name, description, dimensions FROM shop_items WHERE id = ?",
        ("shop-item-1",),
    ).fetchone()

    conn.close()

    assert saved["work_id"] == "work-1"
    assert saved["name"] is None
    assert saved["description"] is None
    assert saved["dimensions"] is None


def test_standalone_shop_item_can_have_own_content(db_connection):
    conn = db_connection()

    prepare_v010(conn)

    create_shop_item(
        conn,
        name="чашка камень",
        description="небольшая керамическая чашка",
        dimensions="8 х 8 х 9см",
        price=3500,
        inventory_type="stock",
        stock_quantity=5,
    )

    saved = conn.execute(
        "SELECT work_id, name, description, dimensions FROM shop_items WHERE id = ?",
        ("shop-item-1",),
    ).fetchone()

    conn.close()

    assert saved["work_id"] is None
    assert saved["name"] == "чашка камень"
    assert saved["description"] == "небольшая керамическая чашка"
    assert saved["dimensions"] == "8 х 8 х 9см"


@pytest.mark.parametrize("invalid_name", [None, "", "   "])
def test_standalone_shop_item_requires_nonempty_name(db_connection, invalid_name):
    conn = db_connection()

    prepare_v010(conn)

    with pytest.raises(sqlite3.IntegrityError):
        create_shop_item(
            conn,
            name=invalid_name,
            price=3500,
            stock_quantity=5,
        )

    conn.rollback()
    conn.close()


@pytest.mark.parametrize(
    ("name", "description", "dimensions"),
    [
        ("Другое имя", None, None),
        (None, "Собственное описание Shop-item", None),
        (None, None, "10 x 10 x 20"),
    ],
)
def test_linked_shop_item_cannot_duplicate_work_content(
    db_connection, name, description, dimensions
):
    conn = db_connection()

    prepare_v010(conn)
    create_work(conn)

    with pytest.raises(sqlite3.IntegrityError):
        create_shop_item(
            conn,
            work_id="work-1",
            name=name,
            description=description,
            dimensions=dimensions,
            price=30000,
            inventory_type="unique",
            stock_quantity=1,
        )

    conn.rollback()
    conn.close()


def test_work_cannot_have_two_linked_shop_items(db_connection):
    conn = db_connection()

    prepare_v010(conn)
    create_work(conn)

    create_shop_item(
        conn,
        shop_item_id="shop-item-1",
        work_id="work-1",
        name=None,
        price=30000,
        inventory_type="unique",
        stock_quantity=1,
    )

    with pytest.raises(sqlite3.IntegrityError):
        create_shop_item(
            conn,
            shop_item_id="shop-item-2",
            work_id="work-1",
            name=None,
            price=35000,
            inventory_type="unique",
            stock_quantity=1,
        )

    conn.rollback()
    conn.close()


@pytest.mark.parametrize(
    ("inventory_type", "stock_quantity"),
    [("unique", 0), ("unique", 1), ("stock", 0), ("stock", 1), ("stock", 15)],
)
def test_shop_item_allows_valid_inventory(
    db_connection, inventory_type, stock_quantity
):
    conn = db_connection()

    prepare_v010(conn)

    create_shop_item(
        conn,
        inventory_type=inventory_type,
        stock_quantity=stock_quantity,
    )

    saved = conn.execute(
        "SELECT inventory_type, stock_quantity FROM shop_items WHERE id = ?",
        ("shop-item-1",),
    ).fetchone()

    conn.close()

    assert saved["inventory_type"] == inventory_type
    assert saved["stock_quantity"] == stock_quantity


@pytest.mark.parametrize("invalid_stock", [2, 5, 100])
def test_unique_shop_item_stock_cannot_exceed_one(db_connection, invalid_stock):
    conn = db_connection()

    prepare_v010(conn)

    with pytest.raises(sqlite3.IntegrityError):
        create_shop_item(
            conn,
            name="Уникальная работа",
            price=30000,
            inventory_type="unique",
            stock_quantity=invalid_stock,
        )

    conn.rollback()
    conn.close()


@pytest.mark.parametrize("inventory_type", ["unique", "stock"])
def test_shop_item_stock_cannot_be_negative(db_connection, inventory_type):
    conn = db_connection()

    prepare_v010(conn)

    with pytest.raises(sqlite3.IntegrityError):
        create_shop_item(
            conn,
            name="Тестовая работа",
            inventory_type=inventory_type,
            stock_quantity=-1,
        )

    conn.rollback()
    conn.close()


@pytest.mark.parametrize(
    "invalid_inventory_type", ["", "reserved", "sold", "warehouse"]
)
def test_shop_item_rejects_unknown_inventory_type(
    db_connection, invalid_inventory_type
):
    conn = db_connection()

    prepare_v010(conn)

    with pytest.raises(sqlite3.IntegrityError):
        create_shop_item(
            conn,
            inventory_type=invalid_inventory_type,
        )

    conn.rollback()
    conn.close()


@pytest.mark.parametrize("valid_price", [0, 1, 30000])
def test_shop_item_allows_nonnegative_price(db_connection, valid_price):
    conn = db_connection()

    prepare_v010(conn)

    create_shop_item(
        conn,
        price=valid_price,
    )

    saved = conn.execute(
        "SELECT price FROM shop_items WHERE id = ?",
        ("shop-item-1",),
    ).fetchone()

    conn.close()

    assert saved["price"] == valid_price


@pytest.mark.parametrize("invalid_price", [-1, -1000])
def test_shop_item_rejects_negative_prices(db_connection, invalid_price):
    conn = db_connection()

    prepare_v010(conn)

    with pytest.raises(sqlite3.IntegrityError):
        create_shop_item(
            conn,
            price=invalid_price,
        )

    conn.rollback()
    conn.close()


def test_shop_item_requires_price(db_connection):
    conn = db_connection()

    prepare_v010(conn)

    with pytest.raises(sqlite3.IntegrityError):
        create_shop_item(
            conn,
            price=None,
        )

    conn.rollback()
    conn.close()


def test_shop_item_has_safe_default_state(db_connection):
    conn = db_connection()

    prepare_v010(conn)

    create_shop_item(
        conn,
        stock_quantity=5,
    )

    saved = conn.execute(
        "SELECT is_published, is_orderable, is_retired FROM shop_items WHERE id = ?",
        ("shop-item-1",),
    ).fetchone()

    conn.close()

    assert saved["is_published"] == 0
    assert saved["is_orderable"] == 0
    assert saved["is_retired"] == 0


def test_shop_item_allows_boolean_flags_to_be_enabled(db_connection):
    conn = db_connection()

    prepare_v010(conn)

    conn.execute(
        """
        INSERT INTO shop_items
            (id, name, price, inventory_type, stock_quantity, is_published, is_orderable, is_retired)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("shop-item-1", "Тестовый товар", 1000, "stock", 5, 1, 1, 1),
    )

    saved = conn.execute(
        "SELECT is_published, is_orderable, is_retired FROM shop_items WHERE id = ?",
        ("shop-item-1",),
    ).fetchone()

    conn.close()

    assert saved["is_published"] == 1
    assert saved["is_orderable"] == 1
    assert saved["is_retired"] == 1


@pytest.mark.parametrize(
    ("is_published", "is_orderable", "is_retired"),
    [(2, 0, 0), (-1, 0, 0), (0, 2, 0), (0, -1, 0), (0, 0, 2), (0, 0, -1)],
)
def test_shop_item_rejects_invalid_boolean_values(
    db_connection, is_published, is_orderable, is_retired
):
    conn = db_connection()

    prepare_v010(conn)

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO shop_items
                (id, name, price, inventory_type, stock_quantity, is_published, is_orderable, is_retired)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "shop-item-1",
                "Тестовый товар",
                1000,
                "stock",
                5,
                is_published,
                is_orderable,
                is_retired,
            ),
        )

    conn.rollback()
    conn.close()


def test_linked_shop_item_required_existing_work(db_connection):
    conn = db_connection()

    prepare_v010(conn)

    with pytest.raises(sqlite3.IntegrityError):
        create_shop_item(
            conn,
            work_id="missing-work",
            name=None,
            price=30000,
            inventory_type="unique",
            stock_quantity=1,
        )

    conn.rollback()
    conn.close()


def test_work_cannot_be_deleted_while_linked_to_shop_item(db_connection):
    conn = db_connection()

    prepare_v010(conn)
    create_work(conn)

    create_shop_item(
        conn,
        work_id="work-1",
        name=None,
        price=30000,
        inventory_type="unique",
        stock_quantity=1,
    )

    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM works WHERE id = ?", ("work-1",))

    saved_work = conn.execute(
        "SELECT id FROM works WHERE id = ?", ("work-1",)
    ).fetchone()
    saved_shop_item = conn.execute(
        "SELECT id, work_id FROM shop_items WHERE id = ?", ("shop-item-1",)
    ).fetchone()

    conn.rollback()
    conn.close()

    assert saved_work["id"] == "work-1"
    assert saved_shop_item["id"] == "shop-item-1"
    assert saved_shop_item["work_id"] == "work-1"


def test_shop_item_images_requires_existing_shop_items(db_connection):
    conn = db_connection()

    prepare_v010(conn)

    with pytest.raises(sqlite3.IntegrityError):
        create_shop_item_image(conn, shop_item_id="missing-shop-item")

    conn.rollback()
    conn.close()


@pytest.mark.parametrize("invalid_position", [0, -1, -10])
def test_shop_item_images_position_must_be_positive(db_connection, invalid_position):
    conn = db_connection()

    prepare_v010(conn)
    create_shop_item(conn)

    with pytest.raises(sqlite3.IntegrityError):
        create_shop_item_image(conn, position=invalid_position)

    conn.rollback()
    conn.close()


def test_shop_item_images_cannot_share_position(db_connection):
    conn = db_connection()

    prepare_v010(conn)

    create_shop_item(conn)
    create_shop_item_image(conn, image_path="first.jpg", position=1)

    with pytest.raises(sqlite3.IntegrityError):
        create_shop_item_image(conn, image_path="second.jpg", position=1)

    conn.rollback()
    conn.close()


def test_deleting_shop_item_deletes_its_images(db_connection):
    conn = db_connection()

    prepare_v010(conn)
    create_shop_item(conn)
    create_shop_item_image(conn, image_path="first.jpg", position=1)
    create_shop_item_image(conn, image_path="second.jpg", position=2)

    conn.commit()

    conn.execute("DELETE FROM shop_items WHERE id = ?", ("shop-item-1",))

    saved_images = conn.execute(
        "SELECT id FROM shop_item_images WHERE shop_item_id = ?", ("shop-item-1",)
    ).fetchall()

    conn.close()

    assert saved_images == []


def test_shop_item_category_relation_cannot_be_duplicated(db_connection):
    conn = db_connection()

    prepare_v010(conn)
    create_shop_item(conn)
    category_id = create_category(conn)

    link_shop_item_to_category(conn, "shop-item-1", category_id)

    with pytest.raises(sqlite3.IntegrityError):
        link_shop_item_to_category(conn, "shop-item-1", category_id)

    conn.rollback()
    conn.close()


def test_shop_item_tag_relation_cannot_be_duplicated(db_connection):
    conn = db_connection()

    prepare_v010(conn)
    create_shop_item(conn)
    tag_id = create_tag(conn)

    link_shop_item_to_tag(conn, "shop-item-1", tag_id)

    with pytest.raises(sqlite3.IntegrityError):
        link_shop_item_to_tag(conn, "shop-item-1", tag_id)

    conn.rollback()
    conn.close()


def test_shop_item_material_relation_cannot_be_duplicated(db_connection):
    conn = db_connection()

    prepare_v010(conn)
    create_shop_item(conn)
    material_id = create_material(conn)

    link_shop_item_to_material(conn, "shop-item-1", material_id)

    with pytest.raises(sqlite3.IntegrityError):
        link_shop_item_to_material(conn, "shop-item-1", material_id)

    conn.rollback()
    conn.close()


def test_deleting_shop_item_deletes_its_dictionary_relations(db_connection):
    conn = db_connection()

    prepare_v010(conn)
    create_shop_item(conn)
    category_id = create_category(conn)
    tag_id = create_tag(conn)
    material_id = create_material(conn)

    link_shop_item_to_category(conn, "shop-item-1", category_id)
    link_shop_item_to_tag(conn, "shop-item-1", tag_id)
    link_shop_item_to_material(conn, "shop-item-1", material_id)

    conn.commit()

    conn.execute("DELETE FROM shop_items WHERE id = ?", ("shop-item-1",))

    category_links = conn.execute(
        "SELECT * FROM shop_item_categories WHERE shop_item_id = ?", ("shop-item-1",)
    ).fetchall()

    tag_links = conn.execute(
        "SELECT * FROM shop_item_tags WHERE shop_item_id = ?", ("shop-item-1",)
    ).fetchall()

    material_links = conn.execute(
        "SELECT * FROM shop_item_materials WHERE shop_item_id = ?", ("shop-item-1",)
    ).fetchall()

    conn.close()

    assert category_links == []
    assert tag_links == []
    assert material_links == []


def test_used_category_cannot_be_deleted(db_connection):
    conn = db_connection()

    prepare_v010(conn)
    create_shop_item(conn)
    category_id = create_category(conn)
    link_shop_item_to_category(conn, "shop-item-1", category_id)

    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))

    conn.rollback()
    conn.close()


def test_used_material_cannot_be_deleted(db_connection):
    conn = db_connection()

    prepare_v010(conn)
    create_shop_item(conn)
    material_id = create_material(conn)
    link_shop_item_to_material(conn, "shop-item-1", material_id)

    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM materials WHERE id = ?", (material_id,))

    conn.rollback()
    conn.close()


def test_deleting_tag_deletes_its_shop_item_relation(db_connection):
    conn = db_connection()

    prepare_v010(conn)
    create_shop_item(conn)
    tag_id = create_tag(conn)
    link_shop_item_to_tag(conn, "shop-item-1", tag_id)

    conn.commit()

    conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))

    saved_relation = conn.execute(
        "SELECT * FROM shop_item_tags WHERE shop_item_id = ? AND tag_id = ?",
        ("shop-item-1", tag_id),
    ).fetchone()

    saved_shop_item = conn.execute(
        "SELECT id FROM shop_items WHERE id = ?", ("shop-item-1",)
    ).fetchone()

    conn.close()

    assert saved_relation is None
    assert saved_shop_item["id"] == "shop-item-1"
