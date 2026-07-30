from flask.sessions import SecureCookieSession

import services.cart_service as cart_service

def test_remove_ordered_items_from_cart_removes_only_requested_products():
    
    session = SecureCookieSession({
        "cart": {
            "product-1": 1,
            "product-2": 2,
            "product-3": 3
        }
    })
    
    product_ids = ["product-1", "product-3"]
    
    result = cart_service.remove_ordered_items_from_cart(session, product_ids)
    
    assert result is True
    assert session["cart"] == {
        "product-2": 2
    }
    assert session.modified is True
    

def test_remove_ordered_items_from_cart_returns_false_when_products_not_found():
    session = SecureCookieSession({"cart": {"product-1": 1}})
    
    product_ids = ["product-2"]
    
    result = cart_service.remove_ordered_items_from_cart(session, product_ids)
    
    assert result is False
    assert session["cart"] == {
        "product-1": 1
    }
    assert session.modified is False
    
    
def test_remove_ordered_items_from_cart_returns_false_for_empty_product_ids():
    session = SecureCookieSession({"cart": {"product-1": 1}})
    
    product_ids = []
    
    result = cart_service.remove_ordered_items_from_cart(session, product_ids)
    
    assert result is False
    assert session["cart"] == {
        "product-1": 1
    }
    assert session.modified is False
    
    
def test_remove_ordered_items_from_cart_returns_false_when_cart_is_empty():
    session = SecureCookieSession({"cart": {}})
    
    product_ids = ["product-1", "product-2"]
    
    result = cart_service.remove_ordered_items_from_cart(session, product_ids)
    
    assert result is False
    assert session["cart"] == {}
    assert session.modified is False