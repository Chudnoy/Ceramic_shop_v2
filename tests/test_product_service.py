import pytest
from werkzeug.datastructures import MultiDict

import services.product_service as product_service
    
    
def create_test_product(
    conn,
    product_id="product-1",
    name="Башня",
    description="Интерьерный объект",
    price=30000,
    img="путь к картинке",
    category_id=1,
    status="available",
    year=2025,
    materials="ceramic",
    is_visible=1,
    is_for_sale=1,
    is_featured=0,
    is_archived=0
):
    conn.execute(
        """
        INSERT INTO products
        (id, name, description, price, img, category_id, status, year, materials, is_visible, is_for_sale, is_featured, is_archived)
        VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (product_id, name, description, price, img, category_id, status, year, materials, is_visible, is_for_sale, is_featured, is_archived)
    )
    
    
def create_test_order(
            conn,
            order_id="order-1",
            customer_name="Денис",
            customer_email="denis@gmail.com",
            customer_phone=None,
            customer_address=None,
            total=30000,
            status="new"
            ):
    conn.execute(
        """
        INSERT INTO orders (id, customer_name, customer_email, customer_phone, customer_address, total, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (order_id, customer_name, customer_email, customer_phone, customer_address, total, status)
    )
    
    
def create_test_order_item(
            conn,
            order_id="order-1",
            product_id="product-1",
            product_name="Башня",
            unit_price=30000,
            quantity=1
            ):
    conn.execute(
        """
        INSERT INTO order_items (order_id, product_id, product_name, unit_price, quantity)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order_id, product_id, product_name, unit_price, quantity)
    )


def create_test_order_with_item(
        conn,
        order_status="new",
        product_status="reserved",
        order_id="order-1",
        product_id="product-1",
        product_name="Башня",
        unit_price=30000,
        quantity=1,
        is_archived=0
):
    create_test_product(
        conn=conn,
        product_id=product_id,
        name=product_name,
        price=unit_price,
        status=product_status,
        is_archived=is_archived
    )
    create_test_order(
        conn=conn,
        order_id=order_id,
        total=unit_price * quantity,
        status=order_status
    )
    create_test_order_item(
        conn=conn,
        order_id=order_id,
        product_id=product_id,
        product_name=product_name,
        unit_price=unit_price,
        quantity=quantity
    )
    
    
def get_saved_product(conn, product_id="product-1"):
    return conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()


def test_process_product_state_form_accepts_valid_data():
    form = {
    "status": "available",
    "is_visible": "1",
    "is_for_sale": "1"
    }
    
    is_valid, message, cleaned_data = product_service.process_product_state_form(form)
    
    assert is_valid is True
    assert message == ""
    assert cleaned_data["status"] == "available"
    assert cleaned_data["is_visible"] == 1
    assert cleaned_data["is_for_sale"] == 1
    assert cleaned_data["is_featured"] == 0
    
    
def test_process_product_state_form_rejects_invalid_status():
    form = {
    "status": "banana",
    "is_visible": "1"
    }
    
    is_valid, message, cleaned_data = product_service.process_product_state_form(form)
    
    assert is_valid is False
    assert message == "Некорректный статус работы"
    assert cleaned_data is None
    
    
def test_process_product_state_form_rejects_featured_when_not_visible():
    form = {
    "status": "available",
    "is_for_sale": "1",
    "is_featured": "1"
    }
    
    is_valid, message, cleaned_data = product_service.process_product_state_form(form)
    
    assert is_valid is False
    assert message == "Чтобы оказаться на главной, работа должна отображаться на сайте"
    assert cleaned_data is None
    
    
def test_process_product_state_form_normalizes_data():
    form = {
    "status": "  SOLD  ",
    "is_visible": "1"
    }
    
    is_valid, message, cleaned_data = product_service.process_product_state_form(form)
    
    assert is_valid is True
    assert message == ""
    assert cleaned_data["status"] == "sold"
    assert cleaned_data["is_visible"] == 1
    assert cleaned_data["is_for_sale"] == 0
    assert cleaned_data["is_featured"] == 0
    
    
def make_valid_product_form():
    return {
        "name": "  Чаша",
        "description": "Фарфоровая работа",
        "price": "12000",
        "category_id": "2",
        "status": "available",
        "year": "2026",
        "materials": "фарфор,  глазурь ",
        "is_visible": "1",
        "is_for_sale": "1",
        "is_featured": "1"
    }
    
def test_process_product_form_accepts_valid_data(monkeypatch):
    
    form = make_valid_product_form()
    
    monkeypatch.setattr(
        product_service,
        "get_category_by_id",
        lambda category_id: {"id": category_id},
    )
    
    is_valid, message, cleaned_data = product_service.process_product_form(form)
    
    assert is_valid is True
    assert message == ""
    assert cleaned_data == {
            "name": "Чаша",
            "description": "Фарфоровая работа",
            "price": 12000,
            "category_id": 2,
            "status": "available",
            "year": 2026,
            "materials": "фарфор, глазурь",
            "is_visible": 1,
            "is_for_sale": 1,
            "is_featured": 1
    }
    
    
def test_process_product_form_rejects_nonexistent_category(monkeypatch):
    form = make_valid_product_form()
    
    monkeypatch.setattr(
            product_service,
            "get_category_by_id",
            lambda category_id: None,
    )
    
    is_valid, message, cleaned_data = product_service.process_product_form(form)
    
    assert is_valid is False
    assert message == "Выбранная категория не существует"
    assert cleaned_data is None
    
    
def test_process_product_form_looks_up_cleaned_category_id(monkeypatch):
    form = make_valid_product_form()
    received_category_ids = []
    
    def fake_get_category_by_id(category_id):
        received_category_ids.append(category_id)
        return {"id": category_id}
        
    monkeypatch.setattr(
            product_service,
            "get_category_by_id",
            fake_get_category_by_id,
    )
    
    is_valid, _, _ = product_service.process_product_form(form)
    
    assert is_valid is True
    assert received_category_ids == [2]
    
    
def test_process_product_form_does_not_look_up_category_when_status_invalid(monkeypatch):
    form = make_valid_product_form()
    form["status"] = "banana"
    received_category_ids = []
    
    def fake_get_category_by_id(category_id):
        received_category_ids.append(category_id)
        return {"id": category_id}
        
    monkeypatch.setattr(
        product_service,
        "get_category_by_id",
        fake_get_category_by_id
    )
    
    is_valid, message, cleaned_data = product_service.process_product_form(form)
    
    assert is_valid is False
    assert message == "Некорректный статус товара"
    assert cleaned_data is None
    assert received_category_ids == []
    
    
def test_process_product_tag_ids_accepts_existing_tags(monkeypatch):
    form = MultiDict([
            ("tag_ids", "1"),
            ("tag_ids", "3")
    ])
    
    monkeypatch.setattr(
            product_service,
            "get_all_tags",
            lambda: [
                    {"id": 1},
                    {"id": 2},
                    {"id": 3}
            ]
    )
    
    is_valid, message, cleaned_tag_ids = product_service.process_product_tag_ids(form)
    
    assert is_valid is True
    assert message == ""
    assert cleaned_tag_ids == [1, 3]
    
    
def test_process_product_tag_ids_rejects_nonexistent_tags(monkeypatch):
    form = MultiDict([
            ("tag_ids", "1"),
            ("tag_ids", "5")
    ])
    
    monkeypatch.setattr(
            product_service,
            "get_all_tags",
            lambda: [
                    {"id": 1},
                    {"id": 2},
                    {"id": 3}
            ]
    )
    
    is_valid, message, cleaned_tag_ids = product_service.process_product_tag_ids(form)
    
    assert is_valid is False
    assert message == "Использованы несуществующие ID тегов"
    assert cleaned_tag_ids == []
    
    
def test_create_products_with_tag_rolls_back_when_tags_fail(empty_db, db_connection, monkeypatch):

    conn = db_connection()
    conn.execute("INSERT INTO categories (id, name, slug) VALUES (?, ?, ?)", (1, 'Чаши', 'bowls'))
    conn.commit()
    conn.close()
    
    test_image_path = "/static/uploads/test-image.jpg"
    
    monkeypatch.setattr(
            product_service,
            "save_image",
            lambda file: (True, "", test_image_path)
    )
    
    deleted_image_paths = []
    
    monkeypatch.setattr(
            product_service,
            "delete_image",
            lambda image_path: deleted_image_paths.append(image_path)
    )
    
    def fail_to_replace_tags(conn, product_id, tag_ids):
        raise RuntimeError("Ошибка сохранения тегов")
        
    monkeypatch.setattr(
            product_service,
            "replace_product_tags",
            fail_to_replace_tags
    )
    
    data = {
        "name": "Тестовая чаша",
        "price": 12000,
        "description": "Описание",
        "category_id": 1,
        "status": "available",
        "year": 2026,
        "materials": "Фарфор",
        "is_visible": 1,
        "is_for_sale": 1,
        "is_featured": 0,
    }
    
    with pytest.raises(RuntimeError, match="Ошибка сохранения тегов"):
        product_service.create_product_with_tags(
                data=data,
                tag_ids=[1, 2],
                file=object()
        )
        
    check_conn = db_connection()
    products_count = check_conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    check_conn.close()
    
    assert products_count == 0
    assert deleted_image_paths == [test_image_path]
    
    
def test_update_product_with_tags_rolls_back_when_tags_fail(empty_db, db_connection, monkeypatch):

    conn = db_connection()
    conn.execute("INSERT INTO categories (id, name, slug) VALUES (?, ?, ?)", (1, 'Чаши', 'bowls'))
    conn.commit()
    conn.close()
    
    product_id = "product-1"
    old_image_path = "/static/uploads/old-image.jpg"
    
    conn = db_connection()
    conn.execute("""
        INSERT INTO
            products 
            (id, name, description, price, img, category_id, status, year, materials, is_visible, is_for_sale, is_featured)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (product_id, "Старая чаша", "Описание", 5000, old_image_path, 1, "sold", 2026, "ceramic", 1, 1, 0))

    conn.commit()
    conn.close()
    
    new_image_path = "/static/uploads/new-image.jpg"
    
    monkeypatch.setattr(
            product_service,
            "save_image",
            lambda file: (True, "", new_image_path)
    )
    
    deleted_image_paths = []
    
    monkeypatch.setattr(
            product_service,
            "delete_image",
            lambda image_path: deleted_image_paths.append(image_path)
    )
    
    monkeypatch.setattr(
        product_service,
        "has_active_order_for_product",
        lambda conn, product_id: False
    )
    
    def fail_to_replace_tags(conn, product_id, tag_ids):
        raise RuntimeError("Ошибка сохранения тегов")
        
    monkeypatch.setattr(
            product_service,
            "replace_product_tags",
            fail_to_replace_tags
    )
    
    data = {
        "name": "Новая чаша",
        "price": 12000,
        "description": "Описание",
        "category_id": 1,
        "status": "available",
        "year": 2026,
        "materials": "Фарфор",
        "is_visible": 1,
        "is_for_sale": 1,
        "is_featured": 0,
    }
    
    with pytest.raises(RuntimeError, match="Ошибка сохранения тегов"):
        product_service.update_product_with_tags(
            product_id=product_id,
            old_image_path=old_image_path,
            data=data,
            tag_ids=[1, 2],
            file=object()
        )
        
    check_conn = db_connection()
    product_after_error = check_conn.execute("SELECT name, img FROM products WHERE id = ?", (product_id,)).fetchone()
    check_conn.close()
    
    assert product_after_error["name"] == "Старая чаша"
    assert product_after_error["img"] == old_image_path
    assert deleted_image_paths == [new_image_path]
    
    
def test_update_product_with_tags_rejects_status_change_when_product_has_active_order(empty_db, db_connection, monkeypatch):
    conn = db_connection()
    conn.execute("INSERT INTO categories (id, name, slug) VALUES (?, ?, ?)", (1, 'Чаши', 'bowls'))
    create_test_product(conn=conn, status="reserved")
    conn.commit()
    conn.close()
    
    monkeypatch.setattr(
        product_service,
        "has_active_order_for_product",
        lambda conn, product_id: True
    )
    
    def fail_if_save_image_called(file):
        raise AssertionError("save_image не должен вызываться")
        
    monkeypatch.setattr(
        product_service,
        "save_image",
        fail_if_save_image_called
    )
    
    data = {"name": "Новое имя", 
                  "price": 50000, 
                  "description": "Интерьерный объект 2", 
                  "category_id": 1, 
                  "year": 2015, 
                  "materials": "ceramic", 
                  'is_visible': 0,
                  'is_for_sale': 0,
                  "is_featured": 0,
                  "status": "available"}
                  
    result = product_service.update_product_with_tags(
            product_id="product-1",
            old_image_path="old_path",
            data=data,
            tag_ids=[1, 2],
            file=object()
            )
            
    assert result == (False, "Нельзя изменить статус работы, связанной с активным заказом")
    
    check_conn = db_connection()
    product_after_error = check_conn.execute("SELECT name, description, price, img, status FROM products WHERE id = ?", ("product-1",)).fetchone()
    check_conn.close()
    
    assert product_after_error["name"] == "Башня"
    assert product_after_error["price"] == 30000
    assert product_after_error["description"] == "Интерьерный объект"
    assert product_after_error["img"] == "путь к картинке"
    assert product_after_error["status"] == "reserved"
    
    
@pytest.mark.parametrize(
    "service_function",
    [
        product_service.archive_product_with_order_check,
        product_service.restore_archived_product,
    ]
)
def test_product_archive_action_returns_error_when_product_not_found(empty_db, db_connection, service_function):
    conn = db_connection()
    conn.execute("INSERT INTO categories (id, name, slug) VALUES (?, ?, ?)", (1, 'Чаши', 'bowls'))
    create_test_product(
        conn=conn,
        product_id="12345"
    )
    conn.commit()
    conn.close()

    is_success, error_message, product_name = service_function("product-1")

    check_conn = db_connection()
    saved_product = get_saved_product(conn=check_conn, product_id="12345")
    check_conn.close()

    assert is_success is False
    assert error_message == "Работа не найдена"
    assert product_name is None
    assert saved_product["is_archived"] == 0


@pytest.mark.parametrize(
    (
        "service_function",
        "initial_is_archived",
        "expected_is_archived",
    ),
    [
        (
            product_service.archive_product_with_order_check,
            0,
            1,
        ),
        (
            product_service.restore_archived_product,
            1,
            0,
        ),
    ]
)
def test_product_archive_action_updates_archived_state(
        empty_db,
        db_connection,
        service_function,
        initial_is_archived,
        expected_is_archived
):
    conn = db_connection()
    conn.execute("INSERT INTO categories (id, name, slug) VALUES (?, ?, ?)", (1, 'Чаши', 'bowls'))
    create_test_product(
        conn=conn,
        is_archived=initial_is_archived
    )
    conn.commit()
    conn.close()

    is_success, error_message, product_name = service_function("product-1")

    check_conn = db_connection()
    saved_product = get_saved_product(conn=check_conn)
    check_conn.close()

    assert is_success is True
    assert error_message == ""
    assert product_name == "Башня"
    assert saved_product["is_archived"] == expected_is_archived


@pytest.mark.parametrize(
    (
        "service_function",
        "initial_is_archived",
        "expected_error_message",
    ),
    [
        (
            product_service.archive_product_with_order_check,
            1,
            "Работа «Башня» уже находится в архиве",
        ),
        (
            product_service.restore_archived_product,
            0,
            "Работа «Башня» уже восстановлена из архива",
        ),
    ]
)
def test_product_archive_action_returns_error_for_invalid_state(
        empty_db,
        db_connection,
        service_function,
        initial_is_archived,
        expected_error_message
):
    conn = db_connection()
    conn.execute("INSERT INTO categories (id, name, slug) VALUES (?, ?, ?)", (1, 'Чаши', 'bowls'))
    create_test_product(
        conn=conn,
        is_archived=initial_is_archived
    )
    conn.commit()
    conn.close()

    is_success, error_message, product_name = service_function("product-1")

    check_conn = db_connection()
    saved_product = get_saved_product(conn=check_conn)
    check_conn.close()

    assert is_success is False
    assert error_message == expected_error_message
    assert product_name is None
    assert saved_product["is_archived"] == initial_is_archived


def test_archive_product_returns_error_when_product_has_active_order(empty_db, db_connection):
    conn = db_connection()
    conn.execute("INSERT INTO categories (id, name, slug) VALUES (?, ?, ?)", (1, 'Чаши', 'bowls'))
    create_test_order_with_item(conn=conn)
    conn.commit()
    conn.close()

    was_archived, error_message, product_name = product_service.archive_product_with_order_check("product-1")

    check_conn = db_connection()
    saved_product = get_saved_product(conn=check_conn)
    check_conn.close()

    assert was_archived is False
    assert error_message == "Нельзя перемещать в архив работу, принадлежащую активному заказу"
    assert product_name is None
    assert saved_product["is_archived"] == 0