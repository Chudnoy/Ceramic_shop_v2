from database import shop_items


def create_test_work(
    conn,
    work_id="work-1",
    name="Башня",
    description="Описание работы",
    dimensions="30 x 20",
    is_published=1,
    project_id=None,
    project_position=None,
):
    conn.execute(
        """
        INSERT INTO works
            (
                id,
                name,
                description,
                dimensions,
                is_published,
                project_id,
                project_position
            )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            work_id,
            name,
            description,
            dimensions,
            is_published,
            project_id,
            project_position,
        ),
    )


def create_test_shop_item(
    conn,
    shop_item_id="shop-1",
    work_id=None,
    name="Кружка",
    description="Описание",
    dimensions="10 x 10",
    price=5000,
    inventory_type="unique",
    stock_quantity=1,
    is_published=1,
    is_orderable=1,
    is_retired=0,
):
    if work_id is not None:
        name = None
        description = None
        dimensions = None

    conn.execute(
        """
        INSERT INTO shop_items (
            id,
            work_id,
            name,
            description,
            dimensions,
            price,
            inventory_type,
            stock_quantity,
            is_published,
            is_orderable,
            is_retired
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            is_published,
            is_orderable,
            is_retired,
        ),
    )


def create_test_category(conn, name="Вазы", slug="vases"):
    return conn.execute(
        "INSERT INTO categories (name, slug) VALUES (?, ?)",
        (name, slug),
    ).lastrowid


def create_test_tag(conn, name="Дом", slug="home"):
    return conn.execute(
        "INSERT INTO tags (name, slug) VALUES (?, ?)",
        (name, slug),
    ).lastrowid


def create_test_material(conn, name="Шамот", slug="chamotte"):
    return conn.execute(
        "INSERT INTO materials (name, slug) VALUES (?, ?)", (name, slug)
    ).lastrowid


def link_work_category(conn, work_id, category_id):
    conn.execute(
        """
        INSERT INTO work_categories (work_id, category_id)
        VALUES (?, ?)
        """,
        (work_id, category_id),
    )


def link_shop_item_category(conn, shop_item_id, category_id):
    conn.execute(
        """
        INSERT INTO shop_item_categories (shop_item_id, category_id)
        VALUES (?, ?)
        """,
        (shop_item_id, category_id),
    )


def link_work_tag(conn, work_id, tag_id):
    conn.execute(
        """
        INSERT INTO work_tags (work_id, tag_id)
        VALUES (?, ?)
        """,
        (work_id, tag_id),
    )


def link_shop_item_tag(conn, shop_item_id, tag_id):
    conn.execute(
        """
        INSERT INTO shop_item_tags (shop_item_id, tag_id)
        VALUES (?, ?)
        """,
        (shop_item_id, tag_id),
    )


def link_work_material(conn, work_id, material_id):
    conn.execute(
        """
        INSERT INTO work_materials (work_id, material_id)
        VALUES (?, ?)
        """,
        (work_id, material_id),
    )


def link_shop_item_material(conn, shop_item_id, material_id):
    conn.execute(
        """
        INSERT INTO shop_item_materials (shop_item_id, material_id)
        VALUES (?, ?)
        """,
        (shop_item_id, material_id),
    )


def test_get_published_shop_items_resolves_linked_and_standalone_items(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_work(conn)

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        work_id="work-1",
        price=30000,
    )
    create_test_shop_item(
        conn,
        shop_item_id="shop-2",
        name="Кружка",
        description="Описание кружки",
    )

    published_items = shop_items.get_published_shop_items(conn, 10)

    conn.close()

    assert [
        (
            item["id"],
            item["name"],
            item["description"],
            item["dimensions"],
        )
        for item in published_items
    ] == [
        (
            "shop-1",
            "Башня",
            "Описание работы",
            "30 x 20",
        ),
        (
            "shop-2",
            "Кружка",
            "Описание кружки",
            "10 x 10",
        ),
    ]


def test_get_published_shop_items_filters_orders_and_limits(empty_db, db_connection):
    conn = db_connection()

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        name="Чашка",
    )
    create_test_shop_item(
        conn,
        shop_item_id="shop-2",
        name="Ваза",
    )
    create_test_shop_item(
        conn,
        shop_item_id="shop-3",
        name="Тарелка",
        is_published=0,
    )
    create_test_shop_item(
        conn,
        shop_item_id="shop-4",
        name="Амфора",
    )

    published_items = shop_items.get_published_shop_items(conn, 2)

    conn.close()

    assert [(item["id"], item["name"]) for item in published_items] == [
        ("shop-4", "Амфора"),
        ("shop-2", "Ваза"),
    ]


def test_get_shop_item_by_id_resolves_linked_item(empty_db, db_connection):
    conn = db_connection()

    create_test_work(conn)

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        work_id="work-1",
        price=30000,
    )

    item = shop_items.get_shop_item_by_id(conn, "shop-1")

    conn.close()

    assert item is not None
    assert item["id"] == "shop-1"
    assert item["work_id"] == "work-1"
    assert item["name"] == "Башня"
    assert item["description"] == "Описание работы"
    assert item["dimensions"] == "30 x 20"
    assert item["price"] == 30000


def test_get_shop_item_by_id_resolves_standalone_item(empty_db, db_connection):
    conn = db_connection()

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        name="Кружка",
        description="Описание кружки",
        dimensions="12 x 8",
        price=5000,
    )

    item = shop_items.get_shop_item_by_id(conn, "shop-1")

    conn.close()

    assert item is not None
    assert item["work_id"] is None
    assert item["name"] == "Кружка"
    assert item["description"] == "Описание кружки"
    assert item["dimensions"] == "12 x 8"
    assert item["price"] == 5000


def test_get_published_shop_item_by_id_returns_published_item(empty_db, db_connection):
    conn = db_connection()

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        name="Кружка",
        is_published=1,
    )

    item = shop_items.get_published_shop_item_by_id(conn, "shop-1")

    conn.close()

    assert item is not None
    assert item["id"] == "shop-1"
    assert item["name"] == "Кружка"


def test_get_published_shop_item_by_id_returns_none_for_unpublished_item(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        name="Кружка",
        is_published=0,
    )

    item = shop_items.get_published_shop_item_by_id(conn, "shop-1")

    conn.close()

    assert item is None


def test_get_shop_item_images_returns_work_images_for_linked_item(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_work(conn)

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        work_id="work-1",
    )

    first_image_id = conn.execute(
        """
        INSERT INTO work_images
            (work_id, image_path, position)
        VALUES (?, ?, ?)
        """,
        ("work-1", "img/tower-detail.jpg", 2),
    ).lastrowid

    second_image_id = conn.execute(
        """
        INSERT INTO work_images
            (work_id, image_path, position)
        VALUES (?, ?, ?)
        """,
        ("work-1", "img/tower.jpg", 1),
    ).lastrowid

    images = shop_items.get_shop_item_images(conn, "shop-1")

    conn.close()

    assert [
        (image["id"], image["image_path"], image["position"]) for image in images
    ] == [
        (second_image_id, "img/tower.jpg", 1),
        (first_image_id, "img/tower-detail.jpg", 2),
    ]


def test_get_shop_item_images_returns_own_images_for_standalone_item(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        name="Кружка",
    )

    first_image_id = conn.execute(
        """
        INSERT INTO shop_item_images
            (shop_item_id, image_path, position)
        VALUES (?, ?, ?)
        """,
        ("shop-1", "img/mug-detail.jpg", 2),
    ).lastrowid

    second_image_id = conn.execute(
        """
        INSERT INTO shop_item_images
            (shop_item_id, image_path, position)
        VALUES (?, ?, ?)
        """,
        ("shop-1", "img/mug.jpg", 1),
    ).lastrowid

    images = shop_items.get_shop_item_images(conn, "shop-1")

    conn.close()

    assert [
        (image["id"], image["image_path"], image["position"]) for image in images
    ] == [
        (second_image_id, "img/mug.jpg", 1),
        (first_image_id, "img/mug-detail.jpg", 2),
    ]


def test_get_shop_item_cover_image_returns_work_cover_for_linked_item(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_work(conn)
    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        work_id="work-1",
    )

    conn.execute(
        """
        INSERT INTO work_images
            (work_id, image_path, position)
        VALUES (?, ?, ?)
        """,
        ("work-1", "img/detail.jpg", 2),
    )

    cover_id = conn.execute(
        """
        INSERT INTO work_images
            (work_id, image_path, position)
        VALUES (?, ?, ?)
        """,
        ("work-1", "img/cover.jpg", 1),
    ).lastrowid

    cover = shop_items.get_shop_item_cover_image(conn, "shop-1")

    conn.close()

    assert cover is not None
    assert (
        cover["id"],
        cover["image_path"],
        cover["position"],
    ) == (
        cover_id,
        "img/cover.jpg",
        1,
    )


def test_get_shop_item_cover_image_returns_own_cover_for_standalone_item(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
    )

    conn.execute(
        """
        INSERT INTO shop_item_images
            (shop_item_id, image_path, position)
        VALUES (?, ?, ?)
        """,
        ("shop-1", "img/detail.jpg", 2),
    )

    cover_id = conn.execute(
        """
        INSERT INTO shop_item_images
            (shop_item_id, image_path, position)
        VALUES (?, ?, ?)
        """,
        ("shop-1", "img/cover.jpg", 1),
    ).lastrowid

    cover = shop_items.get_shop_item_cover_image(conn, "shop-1")

    conn.close()

    assert cover is not None
    assert (
        cover["id"],
        cover["image_path"],
        cover["position"],
    ) == (
        cover_id,
        "img/cover.jpg",
        1,
    )


def test_get_shop_item_cover_image_returns_none_when_cover_does_not_exist(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
    )

    conn.execute(
        """
        INSERT INTO shop_item_images
            (shop_item_id, image_path, position)
        VALUES (?, ?, ?)
        """,
        ("shop-1", "img/detail.jpg", 2),
    )

    cover = shop_items.get_shop_item_cover_image(conn, "shop-1")

    conn.close()

    assert cover is None


def test_get_shop_item_categories_returns_work_categories_for_linked_item(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_work(conn)
    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        work_id="work-1",
    )

    vase_id = create_test_category(conn)
    mugs_id = create_test_category(conn, name="Чашки", slug="mugs")
    plates_id = create_test_category(
        conn,
        name="Тарелки",
        slug="plates",
    )

    link_work_category(conn, "work-1", mugs_id)
    link_work_category(conn, "work-1", vase_id)

    link_shop_item_category(conn, "shop-1", plates_id)

    categories = shop_items.get_shop_item_categories(
        conn,
        "shop-1",
    )

    conn.close()

    assert [(category["name"], category["slug"]) for category in categories] == [
        ("Вазы", "vases"),
        ("Чашки", "mugs"),
    ]


def test_get_shop_item_categories_returns_own_categories_for_standalone_item(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_shop_item(conn, shop_item_id="shop-1")

    mugs_id = create_test_category(conn, name="Чашки", slug="mugs")
    vase_id = create_test_category(conn)

    link_shop_item_category(conn, "shop-1", mugs_id)
    link_shop_item_category(conn, "shop-1", vase_id)

    categories = shop_items.get_shop_item_categories(conn, "shop-1")

    conn.close()

    assert [(category["name"], category["slug"]) for category in categories] == [
        ("Вазы", "vases"),
        ("Чашки", "mugs"),
    ]


def test_get_shop_item_tags_returns_work_tags_for_linked_item(empty_db, db_connection):
    conn = db_connection()

    create_test_work(conn)
    create_test_shop_item(conn, shop_item_id="shop-1", work_id="work-1")

    home_id = create_test_tag(conn)
    memory_id = create_test_tag(conn, name="Память", slug="memory")
    nature_id = create_test_tag(conn, name="Природа", slug="nature")

    link_work_tag(conn, "work-1", memory_id)
    link_work_tag(conn, "work-1", home_id)

    link_shop_item_tag(conn, "shop-1", nature_id)

    tags = shop_items.get_shop_item_tags(conn, "shop-1")

    conn.close()

    assert [(tag["name"], tag["slug"]) for tag in tags] == [
        ("Дом", "home"),
        ("Память", "memory"),
    ]


def test_get_shop_item_materials_returns_own_materials_for_standalone_item(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_shop_item(conn, shop_item_id="shop-1")

    chamotte_id = create_test_material(conn)

    clay_id = create_test_material(
        conn,
        name="Глина",
        slug="clay",
    )

    link_shop_item_material(conn, "shop-1", chamotte_id)
    link_shop_item_material(conn, "shop-1", clay_id)

    materials = shop_items.get_shop_item_materials(conn, "shop-1")

    conn.close()

    assert [(material["name"], material["slug"]) for material in materials] == [
        ("Глина", "clay"),
        ("Шамот", "chamotte"),
    ]


def test_get_shop_item_materials_returns_work_materials_for_linked_item(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_work(conn)
    create_test_shop_item(conn, shop_item_id="shop-1", work_id="work-1")

    chamotte_id = create_test_material(conn)

    clay_id = create_test_material(conn, name="Глина", slug="clay")

    faience_id = create_test_material(conn, name="Фаянс", slug="faience")

    link_work_material(conn, "work-1", chamotte_id)
    link_work_material(conn, "work-1", clay_id)

    link_shop_item_material(conn, "shop-1", faience_id)

    materials = shop_items.get_shop_item_materials(conn, "shop-1")

    conn.close()

    assert [(material["name"], material["slug"]) for material in materials] == [
        ("Глина", "clay"),
        ("Шамот", "chamotte"),
    ]
