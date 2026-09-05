def test_new_public_home_opens(client, empty_db):
    response = client.get("/v2/")

    assert response.status_code == 200
    assert "Полина Яланская" in response.get_data(as_text=True)


def test_public_work_detail_opens(
    client,
    empty_db,
    db_connection,
):
    conn = db_connection()

    conn.execute(
        """
        INSERT INTO works
            (id, slug, name, is_published)
        VALUES (?, ?, ?, ?)
        """,
        ("work-1", "kaplya", "Капля", 1),
    )

    material_id = conn.execute(
        """
        INSERT INTO materials
            (name, slug)
        VALUES (?, ?)
        """,
        ("Шамот", "chamotte"),
    ).lastrowid

    conn.execute(
        """
        INSERT INTO work_materials
            (work_id, material_id)
        VALUES (?, ?)
        """,
        ("work-1", material_id),
    )

    conn.commit()
    conn.close()

    response = client.get("/v2/works/kaplya")

    assert response.status_code == 200
    assert "Капля" in response.get_data(as_text=True)


def test_public_work_detail_returns_404_for_unknown_slug(client, empty_db):
    response = client.get("/v2/works/not-found")

    assert response.status_code == 404


def test_public_work_detailshows_available_status_for_orderable_shop_item(
    client, empty_db, db_connection
):
    conn = db_connection()

    conn.execute(
        """
        INSERT INTO works
            (id, slug, name, is_published)
        VALUES (?, ?, ?, ?)
        """,
        ("work-1", "kaplya", "Капля", 1),
    )

    conn.execute(
        """
        INSERT INTO shop_items
            (id, work_id, price, inventory_type, stock_quantity, is_published, is_orderable, is_retired)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("shop-1", "work-1", 30000, "unique", 1, 1, 1, 0),
    )

    conn.commit()
    conn.close()

    response = client.get("/v2/works/kaplya")
    html = response.get_data(as_text="True")
    assert response.status_code == 200
    assert "Доступна" in html


def test_publick_work_detail_does_not_show_available_status_when_stock_is_reserved(
    client, empty_db, db_connection
):
    conn = db_connection()

    conn.execute(
        """
        INSERT INTO works
            (id, slug, name, is_published)
        VALUES (?, ?, ?, ?)
        """,
        ("work-1", "kaplya", "Капля", 1),
    )

    conn.execute(
        """
        INSERT INTO shop_items
            (id, work_id, price, inventory_type, stock_quantity, is_published, is_orderable, is_retired)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("shop-1", "work-1", 30000, "unique", 1, 1, 1, 0),
    )

    conn.execute(
        """
        INSERT INTO orders
            (id, customer_name, customer_email, total, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("order-1", "Денис", "denis@example.com", 30000, "new"),
    )

    conn.execute(
        """
        INSERT INTO order_items
            (order_id, shop_item_id, product_name, unit_price, quantity)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("order-1", "shop-1", "Капля", 30000, 1),
    )

    conn.commit()
    conn.close()

    response = client.get("/v2/works/kaplya")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Доступна" not in html
