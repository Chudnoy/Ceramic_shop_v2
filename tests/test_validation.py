import pytest

from validation import validate_product


def make_valid_product_data():
    return {
        "name": "чаша",
        "price": 12000,
        "description": "Фарфоровая работа",
        "category_id": 2,
        "year": 2026,
        "materials": "фарфор, глазурь, золото",
        "is_visible": 1,
        "is_for_sale": 0,
        "is_featured": 1,
    }


def test_validate_product_accepts_and_normalizes_valid_data():
    product_data = make_valid_product_data()

    is_valid, message, cleaned_data = validate_product(**product_data)

    assert is_valid is True
    assert message == ""
    assert cleaned_data == {
        "name": "чаша",
        "price": 12000,
        "description": "Фарфоровая работа",
        "category_id": 2,
        "year": 2026,
        "materials": "фарфор, глазурь, золото",
        "is_visible": 1,
        "is_for_sale": 0,
        "is_featured": 1,
    }


@pytest.mark.parametrize(
    "field, invalid_value, expected_message",
    [
        ("price", "два", "Цена должна быть положительным числом"),
        ("name", "    ", "Название обязательно для заполнения"),
        ("year", "1800", "Введите корректный год"),
        ("materials", "", "Материалы обязательны для заполнения"),
        ("description", "", "Описание обязательно для заполнения"),
        ("category_id", "один", "Некорректный ID категории"),
    ],
)
def test_validate_product_rejects_invalid_data(field, invalid_value, expected_message):

    product_data = make_valid_product_data()
    product_data[field] = invalid_value

    is_valid, message, cleaned_data = validate_product(**product_data)

    assert is_valid is False
    assert message == expected_message
    assert cleaned_data == {}
