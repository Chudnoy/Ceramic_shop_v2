from services.public_work_service import get_public_work_page_data


def create_test_work(
    conn,
    work_id="work-1",
    slug="kaplya",
    name="Капля",
    project_id=None,
    project_position=None,
):
    conn.execute(
        """
        INSERT INTO works
            (id, slug, name, project_id, project_position, is_published)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (work_id, slug, name, project_id, project_position, 1),
    )


def create_test_shop_item(
    conn,
    shop_item_id="shop-1",
    work_id="work-1",
    inventory_type="unique",
    stock_quantity=1,
):
    conn.execute(
        """
        INSERT INTO shop_items
            (id, work_id, price, inventory_type, stock_quantity, is_published, is_orderable, is_retired)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (shop_item_id, work_id, 30000, inventory_type, stock_quantity, 1, 1, 0),
    )


def create_test_order(conn, order_id="order-1", status="new"):
    conn.execute(
        """
        INSERT INTO orders
            (id, customer_name, customer_email, total, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order_id, "Денис", "denis@example.com", 30000, status),
    )


def create_test_order_item(conn, order_id="order-1", shop_item_id="shop-1", quantity=1):
    conn.execute(
        """
        INSERT INTO order_items
            (order_id, shop_item_id, product_name, unit_price, quantity)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order_id, shop_item_id, "Капля", 30000, quantity),
    )


def create_test_work_image(
    conn, work_id="work-1", image_path="static/test.jpg", position=1
):
    conn.execute(
        """
        INSERT INTO work_images
            (work_id, image_path, position)
        VALUES (?, ?, ?)
        """,
        (work_id, image_path, position),
    )


def create_test_project(
    conn,
    project_id="project-1",
    name="Пористые формы",
    slug="poristye-formy",
    is_published=1,
):
    conn.execute(
        """
        INSERT INTO projects
            (id, name, slug, intro, period, is_published)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            project_id,
            name,
            slug,
            "Исследование пустоты и формы",
            "2024-2026",
            is_published,
        ),
    )


def create_test_project_image(
    conn, project_id="project-1", image_path="static/project-cover.jpg", position=1
):
    conn.execute(
        """
        INSERT INTO project_images
            (project_id, image_path, position)
        VALUES (?, ?, ?)
        """,
        (project_id, image_path, position),
    )


def test_get_public_work_page_data_returns_no_availability_without_shop_item(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_work(conn)

    conn.commit()
    conn.close()

    page_data = get_public_work_page_data("kaplya")

    assert page_data is not None
    assert page_data["work"]["name"] == "Капля"
    assert page_data["shop_item"] is None
    assert page_data["availability"] is None
    assert page_data["project_preview"] is None


def test_get_public_work_page_data_returns_shop_item_with_availability(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_work(conn)
    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        work_id="work-1",
        inventory_type="stock",
        stock_quantity=3,
    )
    create_test_order(conn)
    create_test_order_item(conn)

    conn.commit()
    conn.close()

    page_data = get_public_work_page_data("kaplya")

    assert page_data is not None
    assert page_data["shop_item"] is not None

    assert page_data["shop_item"]["id"] == "shop-1"
    assert page_data["shop_item"]["stock_quantity"] == 3

    assert page_data["availability"] == {
        "reserved_quantity": 1,
        "available_quantity": 2,
        "can_order": True,
        "stock_state": "available",
    }


def test_get_public_work_page_data_separates_cover_and_detail_images(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_work(conn)
    create_test_work_image(conn)
    create_test_work_image(conn, image_path="static/detail-1", position=2)
    create_test_work_image(conn, image_path="static/detail-2", position=3)
    create_test_work_image(conn, image_path="static/detail-3", position=4)

    conn.commit()
    conn.close()

    page_data = get_public_work_page_data("kaplya")

    assert page_data is not None

    assert page_data["cover_image"]["image_path"] == "static/test.jpg"
    assert page_data["cover_image"]["position"] == 1

    assert [
        (image["image_path"], image["position"]) for image in page_data["detail_images"]
    ] == [("static/detail-1", 2), ("static/detail-2", 3), ("static/detail-3", 4)]


def test_get_public_work_page_data_reurns_project_preview(empty_db, db_connection):
    conn = db_connection()

    create_test_project(conn)
    create_test_project_image(conn)
    create_test_work(
        conn,
        work_id="work-1",
        slug="kaplya",
        name="Капля",
        project_id="project-1",
        project_position=1,
    )
    create_test_work(
        conn,
        work_id="work-2",
        slug="kolonna",
        name="Колонна",
        project_id="project-1",
        project_position=2,
    )
    create_test_work(
        conn,
        work_id="work-3",
        slug="belaya-chasha",
        name="Белая чаша",
        project_id="project-1",
        project_position=3,
    )
    create_test_work_image(
        conn, work_id="work-1", image_path="static/kaplya-cover.jpg", position=1
    )
    create_test_work_image(
        conn, work_id="work-2", image_path="static/kolonna-cover.jpg", position=1
    )
    create_test_work_image(
        conn, work_id="work-3", image_path="static/belaya-cover.jpg", position=1
    )

    conn.commit()
    conn.close()

    page_data = get_public_work_page_data("kaplya")

    assert page_data is not None

    assert page_data["project_preview"] == {
    "id": "project-1",
    "name": "Пористые формы",
    "slug": "poristye-formy",
    "intro": "Исследование пустоты и формы",
    "period": "2024-2026",
    "cover_image_path": "static/project-cover.jpg",
}


def test_get_public_work_page_data_hodes_unpublished_project_preview(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_project(conn, is_published=0)
    create_test_work(conn, project_id="project-1", project_position=1)

    conn.commit()
    conn.close()

    page_data = get_public_work_page_data("kaplya")

    assert page_data is not None
    assert page_data["work"]["name"] == "Капля"
    assert page_data["project_preview"] is None
