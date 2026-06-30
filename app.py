from flask import Flask, session, render_template, request, redirect, url_for, flash
from db import (init_db, get_db_connection, get_reviews_by_product, add_review_db, get_all_products, get_product_by_id, 
                get_products_by_ids, product_exists, get_order_by_id, get_all_orders, create_order, get_all_categories, 
                get_category_by_slug, get_product_with_category, get_products_by_category)
from validation import validate_review
from services.cart_service import get_cart, add_to_cart_serv, remove_from_cart_serv, clear_cart
import uuid
from routes.admin import admin_bp
from routes.main import main_bp
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

init_db()


app = Flask(__name__)
app.register_blueprint(admin_bp)
app.register_blueprint(main_bp)
app.permanent_session_lifetime = timedelta(minutes=30)
app.secret_key = os.environ.get('SECRET_KEY', 'def-secret-key')

@app.context_processor
def inject_cart_count():
    cart = session.get("cart", {})
    return {"cart_count": sum(cart.values())}
    
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)