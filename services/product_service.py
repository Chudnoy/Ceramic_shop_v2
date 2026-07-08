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
    year = form.get("year", 0)
    materials = form.get("materials", "")
    is_visible = 1 if form.get('is_visible') == '1' else 0
    is_for_sale = 1 if form.get('is_for_sale') == '1' else 0
    
    if status not in PRODUCT_STATUSES:
        return False, "Некорректный статус товара", None
        
    is_valid, error_message, cleaned_data = validate_product(name, price, description, category_id, year, materials, is_visible, is_for_sale)
    
    if not is_valid:
        return False, error_message, None
    
    cleaned_data["status"] = status
        
    return True, "", cleaned_data