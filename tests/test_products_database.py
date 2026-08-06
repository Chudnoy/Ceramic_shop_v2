import database.products as products
import database.tags as tags


def create_test_product(
    conn,
    name="Белая ваза",
    price=9999,
    description="Красивая белая ваза",
    img_path="путь к картинке",
    category_id=1,
    status="available",
    year=2009,
    materials="ceramic",
    is_visible=1,
    is_for_sale=1,
    is_featured=0,
):
    product_id = products.insert_product(
        conn=conn,
        name=name,
        price=price,
        description=description,
        img_path=img_path,
        category_id=category_id,
        status=status,
        year=year,
        materials=materials,
        is_visible=is_visible,
        is_for_sale=is_for_sale,
        is_featured=is_featured,
    )
    return product_id


def create_test_category(conn, name="Вазы", slug="vases"):
    conn.execute("INSERT INTO categories (name, slug) VALUES (?, ?)", (name, slug))


def test_created_product_can_be_retrieved(empty_db, db_connection):

    conn = db_connection()
    create_test_category(conn)
    product_id = create_test_product(conn)
    conn.commit()
    conn.close()

    product = products.get_product_by_id(product_id)

    assert product is not None
    assert isinstance(product["id"], str)
    assert product["id"] == product_id
    assert product["name"] == "Белая ваза"
    assert product["price"] == 9999
    assert products.product_exists(product_id) is True
    assert products.product_exists("999") is False
    assert product["status"] == "available"
    assert product["is_visible"] == 1
    assert product["category_id"] == 1


def test_update_product_state_changes_only_product_state(empty_db, db_connection):

    conn = db_connection()
    create_test_category(conn)
    product_id = create_test_product(conn)

    is_updated = products.update_product_state(
        conn=conn,
        product_id=product_id,
        status="sold",
        is_visible=0,
        is_for_sale=0,
        is_featured=1,
    )

    conn.commit()
    conn.close()

    product = products.get_product_by_id(product_id)

    assert is_updated is True

    assert product["status"] == "sold"
    assert product["is_visible"] == 0
    assert product["is_for_sale"] == 0
    assert product["is_featured"] == 1

    assert product["name"] == "Белая ваза"
    assert product["price"] == 9999


def test_set_product_archived_changes_only_archive_setting(empty_db, db_connection):

    conn = db_connection()
    create_test_category(conn)
    product_id = create_test_product(conn)
    conn.commit()
    conn.close()

    assert products.get_product_by_id(product_id)["is_archived"] == 0

    conn = db_connection()

    was_archived = products.set_product_archived(
        conn=conn, product_id=product_id, is_archived=1
    )

    conn.commit()
    conn.close()

    archived_product = products.get_product_by_id(product_id)

    assert was_archived is True
    assert archived_product["is_archived"] == 1

    conn = db_connection()

    was_restored = products.set_product_archived(
        conn=conn, product_id=product_id, is_archived=0
    )

    conn.commit()
    conn.close()

    restored_product = products.get_product_by_id(product_id)

    assert was_restored is True
    assert restored_product["is_archived"] == 0
    assert restored_product["is_visible"] == 1
    assert restored_product["is_for_sale"] == 1


def test_update_product_changes_all_product_data_except_id(empty_db, db_connection):

    conn = db_connection()
    create_test_category(conn)
    product_id = create_test_product(conn)

    create_test_category(conn, name="Чашки", slug="cups")

    conn.commit()
    conn.close()

    conn = db_connection()
    try:
        products.update_product_data(
            conn=conn,
            product_id=product_id,
            name="Чашка",
            price=2500,
            description="Синяя чашка",
            img_path="Другой путь к картинке",
            category_id=2,
            status="reserved",
            year=2022,
            materials="Другие",
            is_visible=0,
            is_for_sale=0,
            is_featured=1,
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    product = products.get_product_by_id(product_id)

    assert product["id"] == product_id
    assert product["name"] == "Чашка"
    assert product["price"] == 2500
    assert product["description"] == "Синяя чашка"
    assert product["img"] == "Другой путь к картинке"
    assert product["category_id"] == 2
    assert product["status"] == "reserved"
    assert product["year"] == 2022
    assert product["materials"] == "Другие"
    assert product["is_visible"] == 0
    assert product["is_for_sale"] == 0
    assert product["is_featured"] == 1


def test_get_product_with_category_returns_correct_data(empty_db, db_connection):

    conn = db_connection()
    create_test_category(conn)
    product_id = create_test_product(conn)
    conn.commit()
    conn.close()

    product = products.get_product_with_category(product_id)

    assert product is not None
    assert product["id"] == product_id
    assert product["name"] == "Белая ваза"
    assert product["price"] == 9999
    assert product["description"] == "Красивая белая ваза"
    assert product["img"] == "путь к картинке"
    assert product["category_id"] == 1
    assert product["status"] == "available"
    assert product["year"] == 2009
    assert product["materials"] == "ceramic"
    assert product["is_visible"] == 1
    assert product["is_for_sale"] == 1
    assert product["is_featured"] == 0
    assert product["category_name"] == "Вазы"
    assert product["category_slug"] == "vases"
    assert products.get_product_with_category(999) is None


def test_get_products_by_category_returns_products_only_in_its_category(
    empty_db, db_connection
):

    conn = db_connection()
    create_test_category(conn)
    create_test_category(conn, name="Чашки", slug="cups")
    create_test_product(conn)
    create_test_product(
        conn,
        name="Сны карелии",
        price=15000,
        description="Про природу",
        img_path="другой путь",
        category_id=1,
        year=2011,
    )
    create_test_product(
        conn,
        name="Детская чашка",
        price=3000,
        description="Розовая чашка",
        img_path="третий путь",
        category_id=2,
        year=2025,
        materials="Глина",
    )
    conn.commit()
    conn.close()

    vases_products = products.get_products_by_category(1)

    vases_product_names = [product["name"] for product in vases_products]

    assert len(vases_products) == 2
    assert set(vases_product_names) == {"Белая ваза", "Сны карелии"}
    assert all(product["category_name"] == "Вазы" for product in vases_products)


def test_get_products_by_ids_returns_correct_products(empty_db, db_connection):

    conn = db_connection()
    create_test_category(conn)
    white_vase_id = create_test_product(conn)
    create_test_product(
        conn,
        name="Сны карелии",
        price=15000,
        description="Про природу",
        img_path="другой путь",
        category_id=1,
        year=2011,
    )
    kids_cup_id = create_test_product(
        conn,
        name="Детская чашка",
        price=3000,
        description="Розовая чашка",
        img_path="третий путь",
        category_id=1,
        year=2025,
        materials="Глина",
    )
    conn.commit()
    conn.close()

    two_products = products.get_products_by_ids([white_vase_id, kids_cup_id])
    two_products_names = {product["name"] for product in two_products}

    assert two_products_names == {"Белая ваза", "Детская чашка"}


def test_get_products_by_ids_returns_empty_list_without_db_call(monkeypatch):

    def fail_if_called():
        raise AssertionError("Подключение к базе не должно вызываться")

    monkeypatch.setattr(products, "get_db_connection", fail_if_called)

    result = products.get_products_by_ids([])

    assert result == []


def test_get_all_products_returns_only_visible_non_archived_products(
    empty_db, db_connection
):

    conn = db_connection()
    create_test_category(conn)
    create_test_product(conn)
    create_test_product(
        conn,
        name="Сны карелии",
        price=15000,
        description="Про природу",
        img_path="другой путь",
        category_id=1,
        year=2011,
        is_visible=0,
    )
    third_id = create_test_product(
        conn,
        name="Детская чашка",
        price=3000,
        description="Розовая чашка",
        img_path="третий путь",
        category_id=1,
        year=2025,
        materials="Глина",
    )

    conn.commit()

    products.set_product_archived(conn=conn, product_id=third_id, is_archived=1)

    conn.commit()
    conn.close()

    all_products = products.get_all_products()

    product_names = {product["name"] for product in all_products}

    assert len(all_products) == 1
    assert product_names == {"Белая ваза"}


def test_get_all_products_returns_non_archived_products(empty_db, db_connection):

    conn = db_connection()
    create_test_category(conn)
    create_test_product(conn)
    create_test_product(
        conn,
        name="Сны карелии",
        price=15000,
        description="Про природу",
        img_path="другой путь",
        category_id=1,
        year=2011,
        is_visible=0,
    )
    third_id = create_test_product(
        conn,
        name="Детская чашка",
        price=3000,
        description="Розовая чашка",
        img_path="третий путь",
        category_id=1,
        year=2025,
        materials="Глина",
        is_visible=1,
    )

    conn.commit()

    products.set_product_archived(conn=conn, product_id=third_id, is_archived=1)

    conn.commit()
    conn.close()

    all_products = products.get_all_products(only_visible=False)

    product_names = {product["name"] for product in all_products}

    assert len(all_products) == 2
    assert product_names == {"Сны карелии", "Белая ваза"}


def test_get_all_products_returns_only_archived_products(empty_db, db_connection):

    conn = db_connection()
    create_test_category(conn)
    first_id = create_test_product(conn)

    create_test_product(
        conn,
        name="Сны карелии",
        price=15000,
        description="Про природу",
        img_path="другой путь",
        category_id=1,
        year=2011,
        is_visible=1,
    )
    third_id = create_test_product(
        conn,
        name="Детская чашка",
        price=3000,
        description="Розовая чашка",
        img_path="третий путь",
        category_id=1,
        year=2025,
        materials="Глина",
        is_visible=0,
    )

    conn.commit()

    products.set_product_archived(conn=conn, product_id=first_id, is_archived=1)

    products.set_product_archived(conn=conn, product_id=third_id, is_archived=1)

    conn.commit()
    conn.close()

    all_products = products.get_all_products(only_visible=False, is_archived=True)

    product_names = {product["name"] for product in all_products}

    assert len(all_products) == 2
    assert product_names == {"Детская чашка", "Белая ваза"}


def test_get_all_products_returns_only_featured_products(empty_db, db_connection):
    conn = db_connection()
    create_test_category(conn)
    create_test_product(conn, is_featured=1)

    create_test_product(
        conn,
        name="Сны карелии",
        price=15000,
        description="Про природу",
        img_path="другой путь",
        category_id=1,
        year=2011,
    )
    create_test_product(
        conn,
        name="Детская чашка",
        price=3000,
        description="Розовая чашка",
        img_path="третий путь",
        category_id=1,
        year=2025,
        materials="Глина",
        is_featured=1,
    )
    conn.commit()
    conn.close()

    all_products = products.get_all_products(only_featured=True)

    product_names = {product["name"] for product in all_products}

    assert len(all_products) == 2
    assert product_names == {"Белая ваза", "Детская чашка"}


def test_get_all_products_returns_only_featured_and_visible_products(
    empty_db, db_connection
):

    conn = db_connection()
    create_test_category(conn)
    create_test_product(conn)
    create_test_product(
        conn,
        name="Сны карелии",
        price=15000,
        description="Про природу",
        img_path="другой путь",
        category_id=1,
        year=2011,
        is_visible=0,
        is_featured=1,
    )
    create_test_product(
        conn,
        name="Детская чашка",
        price=3000,
        description="Розовая чашка",
        img_path="третий путь",
        category_id=1,
        year=2025,
        materials="Глина",
        is_visible=1,
        is_featured=1,
    )
    conn.commit()
    conn.close()

    all_products = products.get_all_products(only_visible=True, only_featured=True)

    product_names = {product["name"] for product in all_products}

    assert product_names == {"Детская чашка"}


def test_get_all_products_filters_by_normalized_status(empty_db, db_connection):

    conn = db_connection()
    create_test_category(conn)
    create_test_product(conn, status="sold")

    create_test_product(
        conn,
        name="Сны карелии",
        price=15000,
        description="Про природу",
        img_path="другой путь",
        category_id=1,
        year=2011,
        status="available",
    )
    create_test_product(
        conn,
        name="Детская чашка",
        price=3000,
        description="Розовая чашка",
        img_path="третий путь",
        category_id=1,
        year=2025,
        materials="Глина",
        status="reserved",
    )
    conn.commit()
    conn.close()

    all_products = products.get_all_products(status="  SOLD ")

    product_names = {product["name"] for product in all_products}

    assert product_names == {"Белая ваза"}


def test_get_all_products_ignores_invalid_status(empty_db, db_connection):

    conn = db_connection()
    create_test_category(conn)
    create_test_product(conn)
    create_test_product(conn, name="Чашка", status="reserved")
    create_test_product(conn, name="Тарелка", status="sold")
    conn.commit()
    conn.close()

    all_products = products.get_all_products(status="aaa")

    product_names = {product["name"] for product in all_products}

    assert product_names == {"Белая ваза", "Чашка", "Тарелка"}


def test_get_all_products_filters_by_category_slug(empty_db, db_connection):

    conn = db_connection()
    create_test_category(conn)
    create_test_category(conn, name="Чашки", slug="cups")

    create_test_product(conn)
    create_test_product(conn, name="Сны Карелии", category_id=1)
    create_test_product(conn, name="Кружка", category_id=2)
    conn.commit()
    conn.close()

    all_products = products.get_all_products(category_slug="vases")

    product_names = {product["name"] for product in all_products}

    assert product_names == {"Белая ваза", "Сны Карелии"}


def test_get_all_products_searches_by_name_and_description(empty_db, db_connection):

    conn = db_connection()
    create_test_category(conn)
    create_test_product(conn, name="Белая ваза", description="Керамический объект")
    create_test_product(
        conn, name="Сны Карелии", description="ваза по природным мотивам"
    )
    create_test_product(conn, name="Кружка", description="Детская кружка")
    conn.commit()
    conn.close()

    all_products = products.get_all_products(search_query="ваза")

    product_names = {product["name"] for product in all_products}

    assert product_names == {"Белая ваза", "Сны Карелии"}


def test_get_all_products_sorts_by_price(empty_db, db_connection):

    conn = db_connection()
    create_test_category(conn)
    create_test_product(conn, price=5000)
    create_test_product(
        conn, name="Сны Карелии", description="На природные мотивы", price=10000
    )
    create_test_product(
        conn, name="Детская кружка", description="Розовая кружка", price=2500
    )
    conn.commit()
    conn.close()

    all_products = products.get_all_products(sort_by="price", order="ASC")

    product_names = [product["name"] for product in all_products]

    assert product_names == ["Детская кружка", "Белая ваза", "Сны Карелии"]

    all_products = products.get_all_products(sort_by="price", order="DESC")

    product_names = [product["name"] for product in all_products]

    assert product_names == ["Сны Карелии", "Белая ваза", "Детская кружка"]


def test_get_all_products_ignores_invalid_sort_data(empty_db, db_connection):

    conn = db_connection()
    create_test_category(conn)
    create_test_product(conn, price=5000)
    create_test_product(
        conn, name="Сны Карелии", description="На природные мотивы", price=10000
    )
    create_test_product(
        conn, name="Детская кружка", description="Розовая кружка", price=2500
    )
    conn.commit()
    conn.close()

    all_products = products.get_all_products(sort_by="banana", order="sideways")

    product_names = [product["name"] for product in all_products]

    assert product_names == ["Белая ваза", "Детская кружка", "Сны Карелии"]


def test_delete_product_completely_removes_product_dependencies(
    empty_db, db_connection
):

    conn = db_connection()
    create_test_category(conn)
    product_id = create_test_product(conn)
    conn.commit()
    conn.close()

    tags.create_tag("Природа", "nature")

    tag_id = tags.get_tag_by_slug("nature")["id"]

    tags.add_tag_to_product(product_id, tag_id)

    conn = db_connection()

    try:
        is_deleted = products.delete_product_data(
            conn=conn,
            product_id=product_id,
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    assert is_deleted is True

    product = products.get_product_by_id(product_id)

    assert product is None

    check_conn = db_connection()

    product_tags_count = check_conn.execute(
        """
        SELECT COUNT(*)
        FROM product_tags
        WHERE product_id = ?
        """,
        (product_id,),
    ).fetchone()[0]

    check_conn.close()

    assert product_tags_count == 0


def test_update_product_status_updates_when_status_matches(empty_db, db_connection):

    conn = db_connection()
    create_test_category(conn)
    product_id = create_test_product(conn)
    conn.commit()
    conn.close()

    conn = None

    try:
        conn = db_connection()
        result = products.update_product_status(
            conn=conn,
            product_id=product_id,
            new_status="reserved",
            expected_status="available",
        )
        conn.commit()
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()

    updated_product = products.get_product_by_id(product_id)

    assert result is True
    assert updated_product["status"] == "reserved"


def test_update_product_status_does_not_update_when_status_does_not_match(
    empty_db, db_connection
):

    conn = db_connection()
    create_test_category(conn)
    product_id = create_test_product(conn, status="reserved")
    conn.commit()
    conn.close()

    conn = None

    try:
        conn = db_connection()
        result = products.update_product_status(
            conn=conn,
            product_id=product_id,
            new_status="sold",
            expected_status="available",
        )
        conn.commit()
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()

    updated_product = products.get_product_by_id(product_id)

    assert result is False
    assert updated_product["status"] == "reserved"
