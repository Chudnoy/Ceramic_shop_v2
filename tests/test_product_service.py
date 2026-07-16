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