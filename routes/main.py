from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_all_products, get_all_categories, get_category_by_slug, get_product_with_category, get_reviews_by_product, product_exists, get_product_by_id, get_products_by_ids, add_review_db, create_order, get_order_by_id
from services.cart_service import get_cart, add_to_cart_serv, remove_from_cart_serv, clear_cart
from validation import validate_review
import uuid

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/catalog")
def catalog():
    category_slug = request.args.get('category')
    sort_by = request.args.get("sort_by", "name")
    order = request.args.get("order", "ASC").upper()
    products = get_all_products(category_slug, sort_by, order)
    categories = get_all_categories()

    current_category = None

    if category_slug:
        current_category = get_category_by_slug(category_slug)
        if not current_category:
            flash("Категория не найдена", "error")
            return redirect(url_for('main.catalog'))
    
    return render_template("catalog.html",
                           products=products,
                           categories=categories,
                           current_category=current_category,
                           current_sort=sort_by,
                           current_order=order,
                           category_slug=category_slug)
                           
                           
@main_bp.route('/product/<product_id>')
def product_page(product_id):
    product = get_product_with_category(product_id)
    
    if not product:
        flash("Товар не найден", "error")
        return redirect(url_for("main.catalog"))
        
    reviews = get_reviews_by_product(product_id)
    return render_template("product_page.html", product=product, reviews=reviews)
    
    
@main_bp.route("/add_to_cart/<product_id>", methods=["POST"])
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
        return redirect(url_for("main.catalog"))
        
    new_qty = add_to_cart_serv(session, product_id, quantity)
    product = get_product_by_id(product_id)
    flash(f"Товар «{product['name']}» добавлен в корзину (количество: {new_qty})", "success")
    return redirect(url_for("main.catalog"))
    
    
@main_bp.route("/cart")
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
    
    
@main_bp.route("/remove_from_cart/<product_id>", methods=['POST'])
def remove_from_cart_route(product_id):
    if remove_from_cart_serv(session, product_id):
        flash("Товар удалён из корзины", "info")
    else:
        flash("Товар не найден в корзине", "error")
    return redirect(url_for("main.show_cart"))
    
    
@main_bp.route("/product/<product_id>/review", methods=["POST"])
def add_review(product_id):
    if not product_exists(product_id):
        flash("Товар не найден", "error")
        return redirect(url_for("main.catalog"))
        
    name = request.form.get("name", "").strip()
    rating_str = request.form.get("rating")
    comment = request.form.get("comment", "")
    
    is_valid, error_message, cleaned_data = validate_review(name, rating_str, comment)
    
    if not is_valid:
        flash(error_message, "error")
        return redirect(url_for("main.product_page", product_id=product_id))
        
    add_review_db(product_id, cleaned_data["name"], cleaned_data["rating"], cleaned_data["comment"])
    flash("Спасибо за отзыв", "success")
    
    return redirect(url_for("main.product_page", product_id=product_id))
    
    
@main_bp.route('/checkout')
def checkout_form():
    cart = get_cart(session)
    if not cart:
        flash("Корзина пуста", "error")
        return redirect(url_for("main.catalog"))
    
    product_ids = list(cart.keys())
    products = get_products_by_ids(product_ids)
    total = 0

    for product in products:
        total += product['price'] * cart[product['id']]

    return render_template("checkout.html", products=products, total=total, cart=cart)
    
    
@main_bp.route("/checkout", methods=["POST"])
def checkout_process():
    cart = get_cart(session)
    
    if not cart:
        flash("Корзина пуста", "error")
        return redirect(url_for("main.catalog"))
        
    customer_name = request.form.get("customer_name", "").strip()
    customer_email = request.form.get("customer_email", "").strip()
    customer_phone = request.form.get("customer_phone", "").strip()
    customer_address = request.form.get("customer_address", "").strip()
    
    if not customer_name:
        flash("Имя обязательно для заполнения", "error")
        return redirect(url_for("main.checkout_form"))
    if not customer_email or "@" not in customer_email:
        flash("Введите корректный email", "error")
        return redirect(url_for("main.checkout_form"))
        
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
    
    return redirect(url_for("main.order_success", order_id=order_id))
    
    
@main_bp.route("/order_success/<order_id>")
def order_success(order_id):
    order = get_order_by_id(order_id)
    
    if not order:
        flash("Заказ не найден", "error")
        return redirect(url_for("main.catalog"))
    
    order_items = order.get('items', {})
    
    return render_template("order_success.html", order=order, order_id=order_id, order_items=order_items)