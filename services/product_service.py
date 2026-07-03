from validation import validate_product


PRODUCT_STATUSES = {
"available": "В наличии",
"reserved": "Зарезервировано",
"sold": "Продано",
"hidden": "Скрыт"
}


def process_product_form(form):
    """
Обрабатывает и валидирует форму создания или редактирования товара.

Получает название, описание, цену, категорию и статус из формы. Проверяет, что
статус входит в PRODUCT_STATUSES, а остальные поля передаёт в validate_product.
Возвращает cleaned_data, готовые для create_product или update_product.
"""
    name = form.get("name", "").strip()
    description = form.get("description", "").strip()
    price = form.get("price", 0)
    category_id = form.get("category_id")
    status = form.get("status", "available")
    
    if status not in PRODUCT_STATUSES:
        return False, "Некорректный статус товара", None
        
    is_valid, error_message, cleaned_data = validate_product(name, price, description, category_id)
    
    if not is_valid:
        return False, error_message, None
    
    cleaned_data["status"] = status
        
    return True, "", cleaned_data