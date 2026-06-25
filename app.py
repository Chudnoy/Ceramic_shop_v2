from flask import Flask, session, render_template, request, redirect, url_for, flash
from db import (init_db, get_db_connection, get_reviews_by_product, add_review_db, get_all_products, get_product_by_id, 
                get_products_by_ids, product_exists, get_order_by_id, get_all_orders, create_order, get_all_categories, 
                get_category_by_slug, get_product_with_category, get_products_by_category)
from validation import validate_review
from services.cart_service import get_cart, add_to_cart_serv, remove_from_cart_serv, clear_cart
import uuid

init_db()


app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.context_processor
def inject_cart_count():
    cart = session.get("cart", {})
    return {"cart_count": sum(cart.values())}
    
    
    
@app.route("/")
def index():
    return render_template("index.html")
    
    
@app.route("/catalog")
def catalog():
    category_slug = request.args.get('category')
    sort_by = request.args.get('sort_by', 'products.name')
    order = request.args.get('order', 'asc')
    products = get_all_products(category_slug, sort_by, order)
    categories = get_all_categories()

    current_category = None

    if category_slug:
        current_category = get_category_by_slug(category_slug)
        if not current_category:
            flash("Категория не найдена", "error")
            return redirect(url_for('catalog'))
    
    return render_template("catalog.html",
                           products=products,
                           categories=categories,
                           current_category=current_category,
                           current_sort=sort_by,
                           current_order=order,
                           category_slug=category_slug)
    
    
@app.route('/product/<product_id>')
def product_page(product_id):
    product = get_product_with_category(product_id)
    
    if not product:
        flash("Товар не найден", "error")
        return redirect(url_for("catalog"))
    
    reviews = get_reviews_by_product(product_id)
    return render_template("product_page.html", product=product, reviews=reviews)
        
        
@app.route("/add_to_cart/<product_id>", methods=["POST"])
def add_to_cart_route(product_id):
    quantity_str = request.form.get("quantity", "1")
    
    try:
        quantity = int(quantity_str)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        return "Количество должно быть положительным числом", 400
        
    if not product_exists(product_id):
        flash("Товар не найден", "error")
        return redirect(url_for("catalog"))
        
    new_qty = add_to_cart_serv(session, product_id, quantity)
    product = get_product_by_id(product_id)
    flash(f"Товар «{product['name']}» добавлен в корзину (количество: {new_qty})", "success")
    return redirect(url_for("catalog"))
    
    
@app.route("/cart")
def show_cart():
    cart = get_cart(session)
    if not cart:
        return render_template("cart.html", products=[], total=0, cart={})
    product_ids = list(cart.keys())
    products = get_products_by_ids(product_ids)
    
    total = 0
    
    for product in products:
        total += product["price"] * cart[product["id"]]
        
    return render_template("cart.html", products=products, total=total, cart=cart)
    
    
@app.route("/remove_from_cart/<product_id>")
def remove_from_cart_route(product_id):
    if remove_from_cart_serv(session, product_id):
        flash("Товар удалён из корзины", "info")
    else:
        flash("Товар не найден в корзине", "error")
    return redirect(url_for("show_cart"))
    
    
@app.route("/product/<product_id>/review", methods=["POST"])
def add_review(product_id):
    if not product_exists(product_id):
        flash("Товар не найден", "error")
        return redirect(url_for("catalog"))
        
    name = request.form.get("name", "").strip()
    rating_str = request.form.get("rating")
    comment = request.form.get("comment", "")
    
    is_valid, error_message, cleaned_data = validate_review(name, rating_str, comment)
    
    if not is_valid:
        flash(error_message, "error")
        return redirect(url_for("product_page", product_id=product_id))
        
    add_review_db(product_id, cleaned_data["name"], cleaned_data["rating"], cleaned_data["comment"])
    flash("Спасибо за отзыв", "success")
    
    return redirect(url_for("product_page", product_id=product_id))


@app.route('/checkout')
def checkout_form():
    cart = get_cart(session)
    if not cart:
        flash("Корзина пуста", "error")
        return redirect(url_for("catalog"))
    
    product_ids = list(cart.keys())
    products = get_products_by_ids(product_ids)
    total = 0

    for product in products:
        total += product['price'] * cart[product['id']]

    return render_template("checkout.html", products=products, total=total, cart=cart)
    
    
@app.route("/checkout", methods=["POST"])
def checkout_process():
    cart = get_cart(session)
    
    if not cart:
        flash("Корзина пуста", "error")
        return redirect(url_for("catalog"))
        
    customer_name = request.form.get("customer_name", "").strip()
    customer_email = request.form.get("customer_email", "").strip()
    customer_phone = request.form.get("customer_phone", "").strip()
    customer_address = request.form.get("customer_address", "").strip()
    
    if not customer_name:
        flash("Имя обязательно для заполнения", "error")
        return redirect(url_for("checkout_form"))
    if not customer_email or "@" not in customer_email:
        flash("Введите корректный email", "error")
        return redirect(url_for("checkout_form"))
        
    product_ids = list(cart.keys())
    products = get_products_by_ids(product_ids)
    
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
    
    order_id = str(uuid.uuid4())
    
    create_order(order_id, customer_name, customer_email, customer_phone, customer_address, items_dict, total)
    
    clear_cart(session)
    
    flash(f"Заказ {order_id[:8]} оформлен!", "success")
    
    return redirect(url_for("order_success", order_id=order_id))
    
    
@app.route("/order_success/<order_id>")
def order_success(order_id):
    order = get_order_by_id(order_id)
    
    if not order:
        flash("Заказ не найден", "error")
        return redirect(url_for("catalog"))
    
    order_items = order.get('items', {})
    
    return render_template("order_success.html", order=order, order_id=order_id, order_items=order_items)
    
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)