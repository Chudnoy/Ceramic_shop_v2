from services.public_shop_service import get_public_shop_page_data


def create_test_work(conn, work_id, name, slug=None, is_published=1):
    conn.execute(
        """
        INSERT INTO works
            (id, name, slug, is_published)
        VALUES (?, ?, ?, ?)
        """,
        (work_id, name, slug, is_published),
    )


def create_test_shop_item(
    conn,
    shop_item_id,
    work_id=None,
    name=None,
    price=5000,
    inventory_type="unique",
    stock_quantity=1,
    is_published=1,
    is_orderable=1,
    is_retired=0,
):
    if work_id is not None:
        name = None

    conn.execute(
        """
        INSERT INTO shop_items
            (id, work_id, name, price, inventory_type, stock_quantity, is_published, is_orderable, is_retired)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            shop_item_id,
            work_id,
            name,
            price,
            inventory_type,
            stock_quantity,
            is_published,
            is_orderable,
            is_retired,
        ),
    )


def create_test_order(conn, order_id="order-1", status="new"):
    conn.execute(
        """
        INSERT INTO orders
            (id, customer_name, customer_email, total, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order_id, "Денис", "denis@example.com", 5000, status),
    )


def create_test_work_image(conn, work_id, image_path, position=1):
    conn.execute(
        """
        INSERT INTO work_images
            (work_id, image_path, position)
        VALUES (?, ?, ?)
        """,
        (work_id, image_path, position),
    )


def create_test_shop_item_image(conn, shop_item_id, image_path, position=1):
    conn.execute(
        """
        INSERT INTO shop_item_images
            (shop_item_id, image_path, position)
        VALUES (?, ?, ?)
        """,
        (shop_item_id, image_path, position),
    )


def create_test_order_item(conn, order_id, shop_item_id, quantity=1):
    conn.execute(
        """
        INSERT INTO order_items
            (order_id, shop_item_id, product_name, unit_price, quantity)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order_id, shop_item_id, "Тестовый товар", 5000, quantity),
    )


def test_get_public_shop_page_data_applies_shop_visibility_policy(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_work(conn, work_id="work-available", name="Доступная работа")
    create_test_shop_item(
        conn,
        shop_item_id="shop-available",
        work_id="work-available",
        inventory_type="unique",
        stock_quantity=1,
    )

    create_test_work(conn, work_id="work-reserved", name="Зарезервированная работа")
    create_test_shop_item(
        conn,
        shop_item_id="shop-reserved",
        work_id="work-reserved",
        inventory_type="unique",
        stock_quantity=1,
    )
    create_test_order(conn, order_id="order-reserved", status="new")
    create_test_order_item(
        conn, order_id="order-reserved", shop_item_id="shop-reserved", quantity=1
    )

    create_test_work(conn, work_id="work-sold", name="Проданная работа")
    create_test_shop_item(
        conn,
        shop_item_id="shop-sold",
        work_id="work-sold",
        inventory_type="unique",
        stock_quantity=0,
    )

    create_test_shop_item(
        conn,
        shop_item_id="shop-stock-empty",
        name="Тиражная кружка",
        inventory_type="stock",
        stock_quantity=0,
    )

    create_test_shop_item(
        conn,
        shop_item_id="shop-disabled",
        name="Отключённый товар",
        inventory_type="stock",
        stock_quantity=5,
        is_orderable=0,
    )

    create_test_work(conn, work_id="work-hidden", name="Скрытая работа", is_published=0)
    create_test_shop_item(
        conn,
        shop_item_id="shop-hidden-work",
        work_id="work-hidden",
        inventory_type="unique",
        stock_quantity=1,
    )

    create_test_shop_item(
        conn,
        shop_item_id="shop-retired",
        name="Архивный товар",
        inventory_type="stock",
        stock_quantity=5,
        is_retired=1,
    )

    conn.commit()
    conn.close()

    page_data = get_public_shop_page_data()

    visible_items = {item["id"]: item for item in page_data["shop_items"]}

    assert set(visible_items) == {"shop-available", "shop-reserved", "shop-stock-empty"}

    assert visible_items["shop-available"]["availability"] == {
        "reserved_quantity": 0,
        "available_quantity": 1,
        "can_order": True,
        "stock_state": "available",
    }

    assert visible_items["shop-reserved"]["availability"] == {
        "reserved_quantity": 1,
        "available_quantity": 0,
        "can_order": False,
        "stock_state": "fully_reserved",
    }

    assert visible_items["shop-stock-empty"]["availability"] == {
        "reserved_quantity": 0,
        "available_quantity": 0,
        "can_order": False,
        "stock_state": "out_of_stock",
    }


def test_get_public_shop_page_data_adds_cover_images(empty_db, db_connection):
    conn = db_connection()

    create_test_work(conn, work_id="work-1", name="Башня")
    create_test_shop_item(conn, shop_item_id="shop-linked", work_id="work-1")
    create_test_work_image(
        conn, work_id="work-1", image_path="static/tower-cover.jpg", position=1
    )

    create_test_shop_item(
        conn,
        shop_item_id="shop-standalone",
        name="Кружка",
        inventory_type="stock",
        stock_quantity=5,
    )
    create_test_shop_item_image(
        conn,
        shop_item_id="shop-standalone",
        image_path="static/mug-cover.jpg",
        position=1,
    )

    conn.commit()
    conn.close()

    page_data = get_public_shop_page_data()

    items = {item["id"]: item for item in page_data["shop_items"]}

    assert items["shop-linked"]["cover_image_path"] == "static/tower-cover.jpg"
    assert items["shop-standalone"]["cover_image_path"] == "static/mug-cover.jpg"


def test_get_public_shop_page_data_includes_work_slug_for_linked_item(
    empty_db,
    db_connection,
):
    conn = db_connection()

    create_test_work(
        conn,
        work_id="work-1",
        name="Башня",
        slug="bashnya",
    )

    create_test_shop_item(
        conn,
        shop_item_id="shop-linked",
        work_id="work-1",
    )

    create_test_shop_item(
        conn,
        shop_item_id="shop-standalone",
        name="Кружка",
        inventory_type="stock",
        stock_quantity=5,
    )

    conn.commit()
    conn.close()

    page_data = get_public_shop_page_data()

    items = {item["id"]: item for item in page_data["shop_items"]}

    assert items["shop-linked"]["work_slug"] == "bashnya"
    assert items["shop-standalone"]["work_slug"] is None
