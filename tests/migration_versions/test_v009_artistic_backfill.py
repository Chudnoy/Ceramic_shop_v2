import pytest

import database.migration_versions.v009_backfill_artistic_core as v009
import database.migrations as migrations


def create_legacy_category(conn, name="Скульптура", slug="sculpture"):
    cursor = conn.execute(
        "INSERT INTO categories (name, slug) VALUES (?, ?)", (name, slug)
    )
    return cursor.lastrowid


def create_legacy_tag(conn, name="Природа", slug="nature"):
    cursor = conn.execute("INSERT INTO tags (name, slug) VALUES (?, ?)", (name, slug))

    return cursor.lastrowid


def create_legacy_product(
    conn,
    product_id="product-1",
    name="Работа 1",
    price=10000,
    description=None,
    category_id=None,
    year=None,
    img=None,
    materials="Каменная масса",
    status="available",
    is_visible=1,
    is_archived=0,
):
    conn.execute(
        """
        INSERT INTO products
            (id, name, price, description, category_id, year, img, materials, status, is_visible, is_archived)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            product_id,
            name,
            price,
            description,
            category_id,
            year,
            img,
            materials,
            status,
            is_visible,
            is_archived,
        ),
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


def test_preflight_accepts_valid_material_tokens(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(conn, materials="Каменная масса, глазурь")

    v009.preflight_material_tokens_are_valid(conn)

    conn.close()


@pytest.mark.parametrize(
    "invalid_materials", ["Каменная масса, ", ", глазурь", "Каменная масса,,глазурь"]
)
def test_preflight_rejects_empty_material_tokens(db_connection, invalid_materials):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(conn, materials=invalid_materials)

    with pytest.raises(ValueError):
        v009.preflight_material_tokens_are_valid(conn)

    conn.close()


def test_backfill_materials_creates_canonical_materials(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    v009.backfill_materials(conn)

    saved_materials = conn.execute(
        "SELECT name, slug FROM materials ORDER BY name"
    ).fetchall()

    conn.close()

    assert [(row["name"], row["slug"]) for row in saved_materials] == [
        ("Глазурь", "glaze"),
        ("Каменная масса", "stoneware"),
        ("Фарфор", "porcelain"),
    ]


def test_preflight_accepts_unique_material_tokens(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(
        conn,
        materials="Каменная масса, глазурь",
    )

    v009.preflight_material_tokens_are_unique(conn)

    conn.close()


@pytest.mark.parametrize(
    "materials",
    [
        "Каменная масса, каменная масса",
        "Каменная масса, КАМЕННАЯ МАССА",
        "Каменная масса,   каменная масса ",
    ],
)
def test_preflight_rejects_duplicate_material_tokens(
    db_connection,
    materials,
):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(
        conn,
        materials=materials,
    )

    with pytest.raises(ValueError):
        v009.preflight_material_tokens_are_unique(conn)

    conn.close()


def test_backfill_works_copies_legacy_product_into_work(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(
        conn,
        product_id="work-1",
        name="Башня",
        description="Керамический объект",
        year=2024,
        is_visible=1,
        is_archived=0,
    )

    v009.backfill_works(conn)

    saved_work = conn.execute(
        """
        SELECT id, name, description, year, is_published, project_id, series_id
        FROM works
        WHERE id = ?
        """,
        ("work-1",),
    ).fetchone()

    conn.close()

    assert saved_work["id"] == "work-1"
    assert saved_work["name"] == "Башня"
    assert saved_work["description"] == "Керамический объект"
    assert saved_work["year"] == 2024
    assert saved_work["is_published"] == 1
    assert saved_work["series_id"] is None
    assert saved_work["project_id"] is None


@pytest.mark.parametrize(
    ("is_visible", "is_archived", "expected_is_published"),
    [(1, 0, 1), (1, 1, 0), (0, 0, 0), (0, 1, 0)],
)
def test_backfill_works_maps_legacy_visibility_to_publication(
    db_connection, is_visible, is_archived, expected_is_published
):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(conn, is_visible=is_visible, is_archived=is_archived)

    v009.backfill_works(conn)

    saved_work = conn.execute(
        "SELECT is_published FROM works WHERE id = ?", ("product-1",)
    ).fetchone()

    conn.close()

    assert saved_work["is_published"] == expected_is_published


def test_backfill_work_imageы_copies_legacy_product_image(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(conn, product_id="work-1", img="images/tower.jpg")

    v009.backfill_works(conn)
    v009.backfill_work_images(conn)

    saved_image = conn.execute(
        "SELECT work_id, image_path, position FROM work_images WHERE work_id = ?",
        ("work-1",),
    ).fetchone()

    conn.close()

    assert saved_image["work_id"] == "work-1"
    assert saved_image["image_path"] == "images/tower.jpg"
    assert saved_image["position"] == 1


def test_backfill_work_images_skips_product_without_image(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(conn, img=None)

    v009.backfill_works(conn)
    v009.backfill_work_images(conn)

    image_count = conn.execute("SELECT COUNT(*) FROM work_images").fetchone()[0]

    conn.close()

    assert image_count == 0


def test_backfill_work_categories_copies_legacy_product_categories(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    category_id = create_legacy_category(conn)
    create_legacy_product(conn, product_id="work-1", category_id=category_id)

    v009.backfill_works(conn)
    v009.backfill_work_categories(conn)

    saved_relation = conn.execute(
        "SELECT work_id, category_id FROM work_categories WHERE work_id = ?",
        ("work-1",),
    ).fetchone()

    conn.close()

    assert saved_relation["work_id"] == "work-1"
    assert saved_relation["category_id"] == category_id


def test_backfill_work_categories_skips_product_without_category(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(conn, category_id=None)

    v009.backfill_works(conn)
    v009.backfill_work_categories(conn)

    relation_count = conn.execute("SELECT COUNT(*) FROM work_categories").fetchone()[0]

    conn.close()

    assert relation_count == 0


def test_backfill_work_tags_copies_legacy_product_tags(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    tag_id = create_legacy_tag(conn)
    create_legacy_product(conn, product_id="work-1")

    conn.execute(
        "INSERT INTO product_tags (product_id, tag_id) VALUES (?, ?)",
        ("work-1", tag_id),
    )

    v009.backfill_works(conn)
    v009.backfill_work_tags(conn)

    saved_relation = conn.execute(
        "SELECT work_id, tag_id FROM work_tags WHERE work_id = ?", ("work-1",)
    ).fetchone()

    conn.close()

    assert saved_relation["work_id"] == "work-1"
    assert saved_relation["tag_id"] == tag_id


def test_backfill_work_materials_creates_relations_for_legacy_materials(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    create_legacy_product(
        conn, product_id="work-1", materials="Каменная масса, глазурь"
    )

    v009.backfill_materials(conn)
    v009.backfill_works(conn)
    v009.backfill_work_materials(conn)

    saved_materials = conn.execute(
        """
        SELECT materials.name
        FROM work_materials
        JOIN materials
            ON materials.id = work_materials.material_id
        WHERE work_materials.work_id = ?
        ORDER BY materials.name
        """,
        ("work-1",),
    ).fetchall()

    conn.close()

    assert [row["name"] for row in saved_materials] == ["Глазурь", "Каменная масса"]


def test_v009_backfills_complete_artistic_world(db_connection):
    conn = db_connection()

    migrations.run_migrations(conn, migrations.MIGRATIONS[:8])

    category_id = create_legacy_category(conn, name="Скульптура", slug="sculpture")

    tag_id = create_legacy_tag(conn, name="Архитектура", slug="architecture")

    create_legacy_product(
        conn,
        product_id="work-1",
        name="Башня",
        price=30000,
        description="Керамический объект",
        category_id=category_id,
        year=2024,
        img="images/tower.jpg",
        materials="Каменная масса, глазурь",
        status="available",
        is_visible=1,
        is_archived=0,
    )

    conn.execute(
        "INSERT INTO product_tags (product_id, tag_id) VALUES (?, ?)",
        ("work-1", tag_id),
    )

    v009.apply(conn)

    saved_work = conn.execute(
        """
        SELECT
            id, name, description, year, is_published, project_id, series_id, is_commissionable
        FROM works
        WHERE id = ?
        """,
        ("work-1",),
    ).fetchone()

    saved_image = conn.execute(
        "SELECT work_id, image_path, position FROM work_images WHERE work_id = ?",
        ("work-1",),
    ).fetchone()

    saved_category = conn.execute(
        "SELECT work_id, category_id FROM work_categories WHERE work_id = ?",
        ("work-1",),
    ).fetchone()

    saved_tag = conn.execute(
        "SELECT work_id, tag_id FROM work_tags WHERE work_id = ?", ("work-1",)
    ).fetchone()

    saved_work_materials = conn.execute(
        """
        SELECT materials.name
        FROM work_materials
        JOIN materials
            ON materials.id = work_materials.material_id
        WHERE work_materials.work_id = ?
        ORDER BY materials.name
        """,
        ("work-1",),
    ).fetchall()

    saved_materials = conn.execute(
        "SELECT name, slug FROM materials ORDER BY name"
    ).fetchall()

    legacy_product = conn.execute(
        """
        SELECT
            id,
            name,
            description,
            year,
            img,
            category_id,
            materials
        FROM products
        WHERE id = ?
        """,
        ("work-1",),
    ).fetchone()

    conn.close()

    assert saved_work["id"] == "work-1"
    assert saved_work["name"] == "Башня"
    assert saved_work["description"] == "Керамический объект"
    assert saved_work["year"] == 2024
    assert saved_work["is_published"] == 1

    assert saved_work["project_id"] is None
    assert saved_work["series_id"] is None
    assert saved_work["is_commissionable"] == 0

    assert saved_image["work_id"] == "work-1"
    assert saved_image["image_path"] == "images/tower.jpg"
    assert saved_image["position"] == 1

    assert saved_category["work_id"] == "work-1"
    assert saved_category["category_id"] == category_id

    assert saved_tag["work_id"] == "work-1"
    assert saved_tag["tag_id"] == tag_id

    assert [row["name"] for row in saved_work_materials] == [
        "Глазурь",
        "Каменная масса",
    ]

    assert [(row["name"], row["slug"]) for row in saved_materials] == [
        ("Глазурь", "glaze"),
        ("Каменная масса", "stoneware"),
        ("Фарфор", "porcelain"),
    ]

    assert legacy_product["id"] == "work-1"
    assert legacy_product["name"] == "Башня"
    assert legacy_product["description"] == "Керамический объект"
    assert legacy_product["year"] == 2024
    assert legacy_product["img"] == "images/tower.jpg"
    assert legacy_product["category_id"] == category_id
    assert legacy_product["materials"] == "Каменная масса, глазурь"
