from validation import validate_product
from database.tags import get_all_tags


PRODUCT_STATUSES = {
"available": "В наличии",
"reserved": "Зарезервировано",
"sold": "Продано",
}


def get_product_cart_unavailable_reason(product):
    """
    Возвращает причину, по которой работа недоступна для оформления.

    Если работа доступна, возвращает пустую строку.
    """
    if not product:
        return "Работа не найдена"

    if product["is_archived"] == 1:
        return "Эта работа находится в архиве"

    if product["is_visible"] != 1:
        return "Эта работа сейчас не опубликована"

    if product["is_for_sale"] != 1:
        return "Эта работа не предназначена для продажи"

    if product["status"] == "reserved":
        return "Эта работа уже зарезервирована"

    if product["status"] == "sold":
        return "Эта работа уже продана"

    if product["status"] != "available":
        return "Эта работа сейчас недоступна для продажи"

    return ""


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
    
    
def process_product_tag_ids(form):
    tag_ids = form.getlist("tag_ids")
    
    cleaned_tag_ids = []
    for tag_id in tag_ids:
        try:
            cleaned_tag_ids.append(int(tag_id))
        except ValueError:
            return False, "ID тега должно быть числом", []
            
    existing_ids = {tag["id"] for tag in get_all_tags()}
    
    if not all(tag_id in existing_ids for tag_id in cleaned_tag_ids):
        return False, "Использованы несуществующие ID тегов", []
            
    return True, "", cleaned_tag_ids