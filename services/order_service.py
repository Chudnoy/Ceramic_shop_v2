import uuid
from database.connection import get_db_connection
from database.orders import insert_order, update_order_details
from database.order_items import insert_order_items, update_order_item_quantity


ORDER_STATUSES = {
    'new': 'Новый',
    'processing': 'В работе',
    'completed': 'Выполнен',
    'cancelled': 'Отменён'
}


def process_order_form(form, old_items):
    name = form.get("name", "").strip()
    email = form.get("email", "").strip()
    phone = form.get("phone", "").strip()
    address = form.get("address", "").strip()
    status = form.get('status', 'new')

    if not name:
        return False, 'Имя обязательно для заполнения', None

    if not email or '@' not in email:
        return False, 'Введён некорректный email', None

    if status not in ORDER_STATUSES:
        return False, 'Некорректный статус заказа', None

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
        'status': status
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
            status=data['status']
        )

        if not is_order_updated:
            conn.rollback()
            return False, 'Заказ не найден'
        
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