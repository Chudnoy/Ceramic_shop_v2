import uuid
from database.connection import get_db_connection
from database.orders import insert_order
from database.order_items import insert_order_items


ORDER_STATUSES = {
	'new': 'Новый',
	'processing': 'В работе',
	'completed': 'Выполнен',
	'cancelled': 'Отменён'
}


def process_order_form(form, old_items):
	"""
Обрабатывает и валидирует форму редактирования заказа в админке.

Проверяет имя, email, статус заказа и количество каждого товара. На основе старого
состава заказа собирает обновлённый словарь товаров, пересчитывает итоговую сумму
и возвращает cleaned_data для сохранения заказа в базе данных.
"""
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

	items = {}
	total = 0

	for product_id, product in old_items.items():
		try:
			quantity = int(form.get(f'quantity_{product_id}', 1))
			if quantity < 1:
				raise ValueError
		except (TypeError, ValueError):
			return False, f"Некорректное количество товара для «{product['name']}»", None
		price = int(product['price'])
		subtotal = price * quantity
		total += subtotal

		items[product_id] = {'name': product['name'], 'price': price, 'quantity': quantity}

	cleaned_data = {'name': name, 'email': email, 'phone': phone, 'address': address, 'items': items, 'total': total, 'status': status}

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
    
    
def build_order_items(cart, products):
	"""
Формирует состав заказа и итоговую сумму на основе корзины и списка товаров.

Принимает session-корзину и список товаров, которые должны попасть в заказ.
Для каждого товара берёт количество из корзины, считает subtotal и собирает
словарь items_dict для сохранения в поле orders.items.
"""
	items_dict = {}
	total = 0

	for product in products:
		product_id = product["id"]
		qty = cart[product_id]
		price = product["price"]
		subtotal = price * qty
		total += subtotal
		items_dict[product_id] = {
				"name": product['name'],
				"price": price,
				"quantity": qty
		}

	return items_dict, total


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