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
		return False, 'Введён некоректный email', None
	
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