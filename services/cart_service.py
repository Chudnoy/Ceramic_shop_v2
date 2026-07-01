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

    total = 0

    for product in products:
        total += product['price'] * cart[product['id']]

    return {
        'cart': cart,
        'products': products,
        'total': total,
        'cart_count': cart_count
    }


def get_cart_count(session):
    cart = get_cart(session)
    return sum(cart.values())