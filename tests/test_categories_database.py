import database.categories as categories


def test_delete_category_rejects_deleting_when_it_has_products(empty_db, db_connection):

    categories.create_category("Вазы", "vases", "")
    category_id = categories.get_category_by_slug("vases")["id"]

    conn = db_connection()
    conn.execute(
        "INSERT INTO products (id, name, price, category_id) VALUES (?, ?, ?, ?)",
        (
            "product-1",
            "тестовая работа",
            1000,
            category_id,
        ),
    )
    conn.commit()
    conn.close()

    is_deleted = categories.delete_category(category_id)
    category = categories.get_category_by_id(category_id)

    assert is_deleted is False
    assert category is not None


def test_get_all_categories_with_product_count_returns_correct_counts(
    empty_db, db_connection
):

    categories.create_category("Вазы", "vases", "Красивые вазы")
    categories.create_category("Чашки", "cups", "Красивые чашки")

    vases_category_id = categories.get_category_by_slug("vases")["id"]

    conn = db_connection()
    products = [
        (
            "product-1",
            "Работа-1",
            1000,
            vases_category_id,
        ),
        (
            "product-2",
            "Работа-2",
            2000,
            vases_category_id,
        ),
    ]
    conn.executemany(
        "INSERT INTO products (id, name, price, category_id) VALUES (?, ? ,?, ?)",
        products,
    )
    conn.commit()
    conn.close()

    all_categories = categories.get_all_categories_with_product_count()

    correct_categories = {
        category["slug"]: category
        for category in all_categories
        if category["slug"] in {"vases", "cups"}
    }

    assert len(correct_categories) == 2
    assert correct_categories["vases"]["products_count"] == 2
    assert correct_categories["cups"]["products_count"] == 0


def test_get_all_categories_with_product_count_returns_correct_counts_after_deleting_one_of_products(
    empty_db, db_connection
):
    categories.create_category("Вазы", "vases", "Красивые вазы")
    categories.create_category("Чашки", "cups", "Красивые чашки")

    vases_category_id = categories.get_category_by_slug("vases")["id"]

    conn = db_connection()
    products = [
        (
            "product-1",
            "Работа-1",
            1000,
            vases_category_id,
        ),
        (
            "product-2",
            "Работа-2",
            2000,
            vases_category_id,
        ),
    ]
    conn.executemany(
        "INSERT INTO products (id, name, price, category_id) VALUES (?, ? ,?, ?)",
        products,
    )
    conn.commit()
    conn.close()

    old_all_categories = categories.get_all_categories_with_product_count()
    old_vases_category = next(
        category for category in old_all_categories if category["slug"] == "vases"
    )
    old_cups_category = next(
        category for category in old_all_categories if category["slug"] == "cups"
    )

    conn = db_connection()
    conn.execute("DELETE FROM products WHERE id = ?", ("product-1",))
    conn.commit()
    conn.close()

    new_all_categories = categories.get_all_categories_with_product_count()
    new_vases_category = next(
        category for category in new_all_categories if category["slug"] == "vases"
    )
    new_cups_category = next(
        category for category in new_all_categories if category["slug"] == "cups"
    )

    assert len(old_all_categories) == 2
    assert old_vases_category["products_count"] == 2
    assert old_cups_category["products_count"] == 0
    assert len(new_all_categories) == 2
    assert new_vases_category["products_count"] == 1
    assert new_cups_category["products_count"] == 0


def test_create_category_and_get_by_slug(empty_db):

    categories.create_category(
        "Скульптура", "sculpture", "Объёмные художественные работы"
    )

    category = categories.get_category_by_slug("sculpture")

    assert category is not None
    assert category["name"] == "Скульптура"
    assert category["slug"] == "sculpture"
    assert category["description"] == "Объёмные художественные работы"


def test_get_category_by_slug_returns_none_for_unknown_slug(empty_db):

    category = categories.get_category_by_slug("banana")

    assert category is None


def test_get_category_by_id_returns_correct_category(empty_db):

    categories.create_category("Вазы", "vases", "")
    categories.create_category("Чашки", "cups", "")

    all_categories = categories.get_all_categories()

    cups_category = next(
        (category for category in all_categories if category["slug"] == "cups"), None
    )

    category = categories.get_category_by_id(cups_category["id"])
    assert category is not None
    assert category["id"] == cups_category["id"]
    assert category["name"] == "Чашки"
    assert category["slug"] == "cups"


def test_update_category_updates_fields_and_slug(empty_db):

    categories.create_category("Вазы", "vases", "Красивые вазы")
    old_category_id = categories.get_category_by_slug("vases")["id"]
    categories.update_category("Чашки", "cups", "Красивые чашки", "vases")

    old_category = categories.get_category_by_slug("vases")
    new_category = categories.get_category_by_slug("cups")

    assert old_category is None
    assert new_category is not None
    assert new_category["name"] == "Чашки"
    assert old_category_id == new_category["id"]
    assert new_category["slug"] == "cups"
    assert new_category["description"] == "Красивые чашки"


def test_delete_category_returns_true_and_removes_record(empty_db):

    categories.create_category("Вазы", "vases", "Красивые вазы")
    category_id = categories.get_category_by_slug("vases")["id"]

    is_deleted = categories.delete_category(category_id)

    assert is_deleted is True
    assert categories.get_category_by_id(category_id) is None


def test_delete_category_returns_false_for_unknown_id(empty_db):

    is_deleted = categories.delete_category(987)

    assert is_deleted is False
