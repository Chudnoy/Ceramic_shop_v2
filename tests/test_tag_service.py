from services.tag_service import process_tag_form


def test_process_tag_form_accepts_and_normalized_valid_data():
    form = {
    "tag_name": "  СКУЛЬПТУРА  ",
    "tag_slug": "  CERAMIC-ART   "
    }
    
    is_valid, error_message, cleaned_data = process_tag_form(form)
    
    assert is_valid is True
    assert error_message == ""
    assert cleaned_data == {
    "tag_name": "СКУЛЬПТУРА",
    "tag_slug": "ceramic-art"
    }
    
    
def test_process_tag_form_rejects_invalid_tag_slug():
    form = {
    "tag_name": "Керамика",
    "tag_slug": "ceramic art"
    }
    
    is_valid, error_message, cleaned_data = process_tag_form(form)
    
    assert is_valid is False
    assert error_message == "Slug обязателен и может содержать только латинские буквы, цифры и дефис"
    assert cleaned_data is None
    
    
def test_process_tag_form_rejects_invalid_tag_name():
    form = {
    "tag_name": "       ",
    "tag_slug": "ceramic-art"
    }
    
    is_valid, error_message, cleaned_data = process_tag_form(form)
    
    assert is_valid is False
    assert error_message == "Название тега должно быть заполнено"
    assert cleaned_data is None