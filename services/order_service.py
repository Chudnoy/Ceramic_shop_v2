import uuid

from database.connection import get_db_connection
from database.order_items import (
    get_order_items_by_order_id,
    insert_order_items,
    update_order_item_quantity,
)
from database.orders import (
    delete_order,
    insert_order,
    update_order_details,
    update_order_status,
)
from database.products import update_product_status

ORDER_STATUSES = {
    "new": "Новый",
    "confirmed": "Подтверждён",
    "completed": "Выполнен",
    "canceled": "Отменён",
}
CANCELLABLE_ORDER_STATUSES = ("new", "confirmed")


def process_order_form(form, old_items):
    name = form.get("name", "").strip()
    email = form.get("email", "").strip()
    phone = form.get("phone", "").strip()
    address = form.get("address", "").strip()

    if not name:
        return False, 'Имя обязательно для заполнения', None

    if not email or '@' not in email:
        return False, 'Введён некорректный email', None

    items = []
    total = 0

    for old_item in old_items:
        item_id = old_item['id']

        try:
            quantity = int(form.get(f'quantity_{item_id}', 1))
            if quantity < 1:
                raise ValueError
        except (TypeError, ValueError):
            return False, f"Некорректное количество товара для «{old_item['product_name']}»", None
        
        unit_price = int(old_item['unit_price'])
        subtotal = unit_price * quantity
        total += subtotal

        items.append({
            'id': item_id,
            'quantity': quantity
        })

    cleaned_data = {
        'name': name, 
        'email': email, 
        'phone': phone, 
        'address': address, 
        'items': items, 
        'total': total, 
        }

    return True, '', cleaned_data


def process_checkout_form(form):
    """
Обрабатывает и валидирует форму оформления заказа клиентом.

Получает имя, email, телефон и адрес покупателя из формы. Проверяет обязательное
имя и корректность email. Возвращает очищенные данные покупателя, готовые для
создания заказа.
"""
    customer_name = form.get("customer_name", "").strip()
    customer_email = form.get("customer_email", "").strip()
    customer_phone = form.get("customer_phone", "").strip()
    customer_address = form.get("customer_address", "").strip()

    if not customer_name:
        return False, "Имя обязательно для заполнения", None
    if not customer_email or "@" not in customer_email:
        return False, "Введите корректный email", None
        
    cleaned_data = {
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
            "customer_address": customer_address
        }
        
    return True, "", cleaned_data


def build_order_item_list(cart, available_products):
    items = []
    
    for product in available_products:
        product_id = product["id"]
        quantity = cart.get(product_id, 0)
        
        if quantity <= 0:
            continue
            
        items.append({
                "product_id": product_id,
                "product_name": product["name"],
                "unit_price": product["price"],
                "quantity": quantity
        })
        
    return items


def create_order_with_items(data, items):
    if not items:
        return False, "Нельзя создать пустой заказ", None
        
    order_id = str(uuid.uuid4())
        
    total = sum(item["unit_price"] * item["quantity"] for item in items)
    
    conn = None
    
    try:
        conn = get_db_connection()
        insert_order(
                conn=conn,
                order_id=order_id,
                customer_name=data["customer_name"],
                customer_email=data["customer_email"],
                customer_phone=data["customer_phone"],
                customer_address=data["customer_address"],
                total=total
        )
        
        insert_order_items(
                conn=conn,
                order_id=order_id,
                items=items
        )
        
        for item in items:
            is_reserved = update_product_status(
                conn=conn,
                product_id=item["product_id"],
                new_status="reserved",
                expected_status="available"
            )
            if not is_reserved:
                conn.rollback()
                return False, f"Работа «{item['product_name']}» больше недоступна", None
        
        conn.commit()
        return True, "", order_id
    except Exception:
        if conn is not None:
            conn.rollback()
            
        raise
    finally:
        if conn is not None:
            conn.close()


def update_order_with_items(order_id, data):
    conn = None

    try:
        conn = get_db_connection()

        is_order_updated = update_order_details(
            conn=conn,
            order_id=order_id,
            customer_name=data['name'],
            customer_email=data['email'],
            customer_phone=data['phone'],
            customer_address=data['address'],
            total=data['total'],
            expected_status='new'
        )

        if not is_order_updated:
            conn.rollback()
            return False, 'Заказ не найден или уже нельзя редактировать'
        
        for item in data['items']:
            is_item_updated = update_order_item_quantity(
                conn=conn,
                order_id=order_id,
                item_id=item['id'],
                quantity=item['quantity']
            )

            if not is_item_updated:
                conn.rollback()
                return False, 'Одна из позиций заказа не найдена'
            
        conn.commit()
        
        return True, ''
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()


def confirm_order(order_id):
    conn = None

    try:
        conn = get_db_connection()

        is_order_confirmed = update_order_status(
            conn=conn,
            order_id=order_id,
            new_status='confirmed',
            expected_status='new'
        )

        if not is_order_confirmed:
            conn.rollback()
            return False, 'Заказ не может быть подтверждён'

        conn.commit()
        return True, ''
    except Exception:
        if conn is not None:
            conn.rollback()

        raise
    finally:
        if conn is not None:
            conn.close()


def complete_order(order_id):
    conn = None

    try:
        conn = get_db_connection()
        items = get_order_items_by_order_id(
            conn=conn,
            order_id=order_id
        )

        is_order_completed = update_order_status(
            conn=conn,
            order_id=order_id,
            new_status='completed',
            expected_status='confirmed'
        )

        if not is_order_completed:
            conn.rollback()
            return False, 'Не удалось завершить заказ'

        for item in items:
            product_id = item['product_id']

            if product_id is None:
                continue

            is_sold = update_product_status(
                conn=conn,
                product_id=product_id,
                new_status='sold',
                expected_status='reserved'
            )

            if not is_sold:
                conn.rollback()
                return False, f"Не удалось изменить статус работы «{item['product_name']}»"

        conn.commit()
        return True, ''
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()

            
            
def cancel_order(order_id):
    conn = None
    
    try:
        conn = get_db_connection()
        
        items = get_order_items_by_order_id(conn, order_id)
        
        is_order_canceled = False
        for expected_status in CANCELLABLE_ORDER_STATUSES:
            is_order_canceled = update_order_status(
                conn=conn,
                order_id=order_id,
                new_status="canceled",
                expected_status=expected_status
            )
            if is_order_canceled:
                break
        
        if not is_order_canceled:
            conn.rollback()
            return False, "Заказ не найден или уже не может быть отменён"
        
        for item in items:
            product_id = item["product_id"]
            
            if product_id is None:
                continue
                
            is_released = update_product_status(
                    conn=conn,
                    product_id=product_id,
                    new_status="available",
                    expected_status="reserved"
            )
            
            if not is_released:
                conn.rollback()
                return False, f"Не удалось освободить работу «{item['product_name']}»"
                
        conn.commit()
        return True, ""
    except Exception:
        if conn is not None:
            conn.rollback()
            
        raise
    finally:
        if conn is not None:
            conn.close()


def delete_canceled_order(order_id):
    conn = None

    try:
        conn = get_db_connection()
        is_deleted = delete_order(conn, order_id, 'canceled')

        if not is_deleted:
            conn.rollback()
            return False, 'Удалить можно только отменённый заказ'

        conn.commit()
        return True, ""
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()