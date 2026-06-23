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