from db import get_products_by_ids

def get_cart(session):
    """
Возвращает текущую корзину из session.

Если корзина ещё не создана, возвращает пустой словарь. Корзина хранит id товаров
как ключи и количество выбранных единиц как значения.
"""
    return session.get("cart", {})
    
    
def add_to_cart_serv(session, product_id, quantity):
    """
Добавляет товар в корзину или увеличивает его количество.

Получает текущую корзину из session, увеличивает количество товара на переданное
значение, сохраняет обновлённую корзину обратно в session и помечает session как
изменённую. Возвращает новое количество этого товара в корзине.
"""
    cart = session.get("cart", {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    session["cart"] = cart
    session.modified = True
    return cart[product_id]
    
    
def remove_from_cart_serv(session, product_id):
    """
Удаляет товар из корзины по его id.

Если товар есть в session-корзине, удаляет его, сохраняет обновлённую корзину
и возвращает True. Если товара в корзине нет, ничего не меняет и возвращает False.
"""
    cart = session.get("cart", {})
    if product_id in cart:
        del cart[product_id]
        session["cart"] = cart
        session.modified = True
        return True
    return False
    
    
def clear_cart(session):
    """
Полностью очищает корзину пользователя.

Заменяет session["cart"] на пустой словарь и помечает session как изменённую.
Используется после успешного оформления заказа.
"""
    session["cart"] = {}
    session.modified = True


def build_cart_summary(session):
    """
Собирает подробную сводку текущей корзины.

Загружает товары из базы по id, сохранённым в session, добавляет к каждому товару
служебные поля cart_quantity, cart_item_total и is_available_for_order. Итоговая
сумма считается только по товарам со статусом "available". Недоступные товары
остаются в общем списке корзины, но не попадают в available_products и не входят
в total.
"""
    cart = get_cart(session)
    cart_count = sum(cart.values())

    product_ids = list(cart.keys())
    products = get_products_by_ids(product_ids)
    
    cart_items = []
    available_products = []
    total = 0
    has_unavailable_items = False

    for product in products:
        product_dict = dict(product)
        
        quantity = cart[product_dict['id']]
        item_total = product_dict['price'] * quantity
        is_available_for_order = product_dict['status'] == "available"
        
        product_dict["cart_quantity"] = quantity
        product_dict["cart_item_total"] = item_total
        product_dict["is_available_for_order"] = is_available_for_order
        
        if is_available_for_order:
            available_products.append(product_dict)
            total += item_total
        else:
            has_unavailable_items = True
            
        cart_items.append(product_dict)

    return {
        'cart': cart,
        'products': cart_items,
        'total': total,
        'cart_count': cart_count,
        "has_unavailable_items": has_unavailable_items,
        "available_products": available_products
    }
    
    
def remove_unavailable_items(session):
    """
Удаляет из корзины товары, которые больше нельзя оформить.

Оставляет в session["cart"] только товары, которые существуют в базе данных
и имеют статус "available". Удаляет товары со статусами "reserved", "sold",
"hidden", а также id товаров, которых уже нет в базе. Возвращает True, если
из корзины был удалён хотя бы один товар, иначе False.
"""
    cart = session.get("cart", {})
    
    if not cart:
        return False
        
    cart_products = get_products_by_ids(list(cart.keys()))
    
    available_product_ids = set()
    removed = False
    
    for product in cart_products:
        if product["status"] == "available":
            available_product_ids.add(product["id"])
            
    for product_id in list(cart.keys()):
        if product_id not in available_product_ids:
            del cart[product_id]
            removed = True
            
    if removed:
        session["cart"] = cart
        session.modified = True
        
    return removed
    

def get_cart_count(session):
    """
Возвращает общее количество единиц товаров в корзине.

Суммирует значения из session-корзины. Используется для отображения счётчика
корзины в шапке сайта через context_processor.
"""
    cart = get_cart(session)
    return sum(cart.values())