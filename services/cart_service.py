from db import get_products_by_ids

def get_cart(session):
    return session.get("cart", {})
    
    
def add_to_cart_serv(session, product_id, quantity):
    cart = session.get("cart", {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    session["cart"] = cart
    session.modified = True
    return cart[product_id]
    
    
def remove_from_cart_serv(session, product_id):
    cart = session.get("cart", {})
    if product_id in cart:
        del cart[product_id]
        session["cart"] = cart
        session.modified = True
        return True
    return False
    
    
def clear_cart(session):
    session["cart"] = {}
    session.modified = True


def build_cart_summary(session):
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


def get_cart_count(session):
    cart = get_cart(session)
    return sum(cart.values())