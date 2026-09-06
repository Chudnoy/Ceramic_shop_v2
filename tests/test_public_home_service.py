from services.public_home_service import get_home_page_data


def create_test_work(conn, work_id="work-1", slug="kaplya", name="Капля"):
    conn.execute(
        """
        INSERT INTO works
            (id, slug, name, is_published)
        VALUES (?, ?, ?, ?)
        """,
        (work_id, slug, name, 1),
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


def test_get_home_page_data_adds_availability_to_shop_item(empty_db, db_connection):
    conn = db_connection()

    conn.execute(
        """
        INSERT INTO shop_items
            (id, name, price, inventory_type, stock_quantity, is_published, is_orderable, is_retired)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("shop-1", "Кружка", 6500, "stock", 6, 1, 1, 0),
    )

    conn.execute(
        """
        INSERT INTO orders
            (id, customer_name, customer_email, total, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("order-1", "Денис", "denis@example.com", 13000, "new"),
    )

    conn.execute(
        """
        INSERT INTO order_items
            (order_id, shop_item_id, product_name, unit_price, quantity)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("order-1", "shop-1", "Кружка", 6500, 2),
    )

    conn.commit()
    conn.close()

    page_data = get_home_page_data()

    assert len(page_data["shop_items"]) == 1

    shop_item = page_data["shop_items"][0]

    assert shop_item["id"] == "shop-1"
    assert shop_item["name"] == "Кружка"

    assert shop_item["availability"] == {
        "reserved_quantity": 2,
        "available_quantity": 4,
        "can_order": True,
        "stock_state": "available",
    }


def test_get_home_page_data_returns_only_available_for_order_shop_items(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_work(
        conn,
        work_id="work-1",
        slug="a",
        name="А",
    )
    create_test_work(
        conn,
        work_id="work-2",
        slug="b",
        name="Б",
    )
    create_test_work(
        conn,
        work_id="work-3",
        slug="c",
        name="В",
    )

    create_test_shop_item(
        conn,
        shop_item_id="shop-1",
        work_id="work-1",
        stock_quantity=1,
    )
    create_test_shop_item(
        conn,
        shop_item_id="shop-2",
        work_id="work-2",
        inventory_type="stock",
        stock_quantity=5,
    )
    create_test_shop_item(
        conn, shop_item_id="shop-3", work_id="work-3", stock_quantity=1
    )

    create_test_order(
        conn,
        order_id="order-1",
        status="new",
    )

    create_test_order_item(
        conn,
        order_id="order-1",
        shop_item_id="shop-1",
        quantity=1,
    )

    conn.commit()
    conn.close()

    page_data = get_home_page_data()

    assert [item["id"] for item in page_data["shop_items"]] == [
        "shop-2",
        "shop-3",
    ]
