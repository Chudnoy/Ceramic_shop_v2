import pytest
import sqlite3
from werkzeug.datastructures import MultiDict
import services.product_service as product_service

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
            fake_get_category_by_id,
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
    
    
def test_create_products_with_tag_rolls_back_when_tags_fail(tmp_path, monkeypatch):
    db_path = tmp_path / "test_shop.db"
    conn = sqlite3.connect(db_path)
    
    conn.execute("""
        CREATE TABLE products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            img TEXT,
            category_id INTEGER,
            status TEXT,
            year INTEGER,
            materials TEXT,
            is_visible INTEGER,
            is_for_sale INTEGER,
            is_featured INTEGER
        )
    """)

    conn.commit()
    conn.close()
    
    def get_test_db_connection():
        return sqlite3.connect(db_path)
    
    monkeypatch.setattr(
            product_service,
            "get_db_connection",
            get_test_db_connection
    )
    
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
        
    check_conn = sqlite3.connect(db_path)
    products_count = check_conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    check_conn.close()
    
    assert products_count == 0
    assert deleted_image_paths == [test_image_path]
    
    
def test_update_product_with_tags_rolls_back_when_tags_fail(tmp_path, monkeypatch):
    db_path = tmp_path / "test_shop.db"
    conn = sqlite3.connect(db_path)
    
    conn.execute("""
        CREATE TABLE products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            img TEXT,
            category_id INTEGER,
            status TEXT,
            year INTEGER,
            materials TEXT,
            is_visible INTEGER,
            is_for_sale INTEGER,
            is_featured INTEGER
        )
    """)
    
    product_id = "product-1"
    old_image_path = "/static/uploads/old-image.jpg"
    
    conn.execute("""
        INSERT INTO
            products 
            (id, name, description, price, img, category_id, status, year, materials, is_visible, is_for_sale, is_featured)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (product_id, "Старая чаша", "Описание", 5000, old_image_path, 1, "sold", 2026, "ceramic", 1, 1, 0))

    conn.commit()
    conn.close()
    
    def get_test_db_connection():
        return sqlite3.connect(db_path)
    
    monkeypatch.setattr(
            product_service,
            "get_db_connection",
            get_test_db_connection
    )
    
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
        
    check_conn = sqlite3.connect(db_path)
    product_after_error = check_conn.execute("SELECT name, img FROM products WHERE id = ?", (product_id,)).fetchone()
    check_conn.close()
    
    assert product_after_error == ("Старая чаша", old_image_path)
    assert deleted_image_paths == [new_image_path]