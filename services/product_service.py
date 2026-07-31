from validation import validate_product
from database.connection import get_db_connection
from database.products import insert_product, update_product_data, delete_product_data, update_product_state, get_product_by_id, set_product_archived
from database.tags import get_all_tags, replace_product_tags
from services.image_service import save_image, delete_image
from database.categories import get_category_by_id
from database.orders import has_active_order_for_product


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
    is_featured = 1 if form.get("is_featured") == "1" else 0
    
    if status not in PRODUCT_STATUSES:
        return False, "Некорректный статус товара", None
        
    if not is_visible and is_featured:
        return False, "Работу нельзя добавить на главную, пока она скрыта с сайта", None
        
    is_valid, error_message, cleaned_data = validate_product(name, price, description, category_id, year, materials, is_visible, is_for_sale, is_featured)
    
    if not is_valid:
        return False, error_message, None
        
    category = get_category_by_id(cleaned_data["category_id"])
    
    if not category:
        return False, "Выбранная категория не существует", None
    
    cleaned_data["status"] = status
        
    return True, "", cleaned_data
    
    
def process_product_state_form(form):
    status = form.get("status", "").strip().lower()
    
    is_visible = 1 if form.get("is_visible") == "1" else 0
    is_for_sale = 1 if form.get("is_for_sale") == "1" else 0
    is_featured = 1 if form.get("is_featured") == "1" else 0
    
    if status not in PRODUCT_STATUSES:
        return False, "Некорректный статус работы", None 
        
    if not is_visible and is_featured:
        return False, "Чтобы оказаться на главной, работа должна отображаться на сайте", None
        
    cleaned_data = {
    "status": status,
    "is_visible": is_visible,
    "is_for_sale": is_for_sale,
    "is_featured": is_featured
    }
    
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
    
    
def create_product_with_tags(data, tag_ids, file):
    image_success, image_error, image_path = save_image(file)
    
    if not image_success:
        return False, image_error, None
        
    conn = None
    
    try:
        conn = get_db_connection()
        
        product_id = insert_product(
                conn=conn,
                name=data["name"],
                price=data["price"],
                description=data["description"],
                img_path=image_path,
                category_id=data["category_id"],
                status=data["status"],
                year=data["year"],
                materials=data["materials"],
                is_visible=data["is_visible"],
                is_for_sale=data["is_for_sale"],
                is_featured=data["is_featured"]
        )
    
        replace_product_tags(
            conn=conn,
            product_id=product_id,
            tag_ids=tag_ids
        )
        conn.commit()
        return True, "", product_id
    except Exception:
        if conn is not None:
            conn.rollback()
        delete_image(image_path)
        raise
    finally:
        if conn is not None:
            conn.close()
            
            
def update_product_with_tags(
            product_id,
            old_image_path,
            data,
            tag_ids,
            file
):
    
    conn = None
    new_image_path = None
    
    try:
        conn = get_db_connection()
        
        has_active_order = has_active_order_for_product(
            conn=conn,
            product_id=product_id
        )

        if has_active_order and data["status"] != "reserved":
            return False, "Нельзя изменить статус работы, связанной с активным заказом"
            
        image_success, image_error, new_image_path = save_image(file)
    
        if not image_success:
            return False, image_error
        
        final_image_path = new_image_path or old_image_path
        
        update_product_data(
            conn=conn,
            product_id=product_id,
            name=data["name"],
            price=data["price"],
            description=data["description"],
            img_path=final_image_path,
            category_id=data["category_id"],
            status=data["status"],
            year=data["year"],
            materials=data["materials"],
            is_visible=data["is_visible"],
            is_for_sale=data["is_for_sale"],
            is_featured=data["is_featured"]
        )
        
        replace_product_tags(
            conn=conn,
            product_id=product_id,
            tag_ids=tag_ids
        )
        
        conn.commit()
    except Exception:
        if conn is not None:
            conn.rollback()
        if new_image_path:
            delete_image(new_image_path)
        raise
    finally:
        if conn is not None:
            conn.close()
            
    if new_image_path and old_image_path != new_image_path:
        delete_image(old_image_path)
        
    return True, ""
    
    
def delete_product_with_image(product_id, image_path):
    conn = None
    
    try:
        conn = get_db_connection()
        if has_active_order_for_product(conn=conn, product_id=product_id):
            conn.rollback()
            return False, "Нельзя удалить работу, связанную с активным заказом"
        is_deleted = delete_product_data(conn, product_id)
        conn.commit()
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()
        
    if not is_deleted:
        return False, "Товар не найден"
        
    try:
        delete_image(image_path)
    except OSError:
        return True, "Товар удалён, но файл изображения удалить не удалось"
        
    return True, ""


def update_product_state_with_order_check(product_id, data):
    conn = None

    try:
        conn = get_db_connection()

        has_active_order = has_active_order_for_product(
            conn=conn,
            product_id=product_id
        )

        if has_active_order and data["status"] != "reserved":
            conn.rollback()
            return False, "Нельзя изменить статус работы, связанной с активным заказом"

        is_updated = update_product_state(
            conn=conn,
            product_id=product_id,
            status=data["status"],
            is_visible=data["is_visible"],
            is_for_sale=data["is_for_sale"],
            is_featured=data["is_featured"]
        )

        if not is_updated:
            conn.rollback()
            return False, "Работа не найдена"

        conn.commit()
        return True, ""

    except Exception:
        if conn is not None:
            conn.rollback()
        raise

    finally:
        if conn is not None:
            conn.close()
            
            
def archive_product_with_order_check(product_id):
    
    product = get_product_by_id(product_id)
    
    if not product:
        return False, "Работа не найдена", None
        
    if product["is_archived"] == 1:
        return False, f"Работа «{product['name']}» уже находится в архиве", None
        
    conn = None
    
    try:
        conn = get_db_connection()
        
        if has_active_order_for_product(conn, product_id):
            return False, "Нельзя перемещать в архив работу, принадлежащую активному заказу", None
        
        is_updated = set_product_archived(conn, product_id, 1)
        
        if not is_updated:
            conn.rollback()
            return False, "Работа не найдена", None
            
        conn.commit()
        return True, "", product["name"]
    except Exception:
        if conn is not None:
            conn.rollback()
        
        raise
    finally:
        if conn is not None:
            conn.close()
            
            
def restore_archived_product(product_id):
    product = get_product_by_id(product_id)
    
    if not product:
        return False, "Работа не найдена", None
        
    if product["is_archived"] == 0:
        return False, f"Работа «{product['name']}» уже восстановлена из архива", None
        
    conn = None
    
    try:
        conn = get_db_connection()
        
        is_updated = set_product_archived(conn, product_id, 0)
        
        if not is_updated:
            conn.rollback()
            return False, "Работа не найдена", None
            
        conn.commit()
        return True, "", product["name"]
    except Exception:
        if conn is not None:
            conn.rollback()
        
        raise
    finally:
        if conn is not None:
            conn.close()