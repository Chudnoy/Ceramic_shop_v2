from flask import Flask, session, render_template, request, redirect, url_for, flash
from db import init_db, get_db_connection, get_reviews_by_product, add_review_db, get_all_products, get_product_by_id, get_products_by_ids, product_exists, get_order_by_id, get_all_orders, create_order
from helpers import render_flash
from validation import validate_review
from services.cart_service import get_cart, add_to_cart_serv, remove_from_cart_serv, clear_cart
import uuid

init_db()


app = Flask(__name__)
app.secret_key = "supersecretkey"


@app.route("/")
def index():
    return "Hello ceramic shop"
    
    
@app.route("/catalog")
def catalog():
    products = get_all_products()
    html = render_flash()
    html += "<h1>Каталог товаров</h1>"
    
    for p in products:
        html += f"""
            <div>
                    <h3>{p['name']}</h3>
                    <p>{p['description']}</p>
                    <p>Цена: {p['price']} руб.</p>
                    <a href="/product/{p['id']}">Узнать подробнее</a>
                    <form action="/add_to_cart/{p['id']}" method="POST" style="display: inline;">
                            <input type="number" name="quantity" value="1" min="1" style="width: 50px;">
                            <button type="submit">Добавить в корзину</button>
                    </form>
            </div>
            <hr>
        """
    html += "<a href='/cart'>Перейти в корзину</a>"
    return html
    
    
@app.route('/product/<product_id>')
def product_page(product_id):
    product = get_product_by_id(product_id)
    
    if not product:
        return "Товар не найден", 404
    
    reviews = get_reviews_by_product(product_id)
    if product:
        html = render_flash()
        html += f"<h1>{product['name']}</h1><p>{product['description']}</p><p>Цена: {product['price']} руб.</p>"
        html += "<h2>Отзывы</h2>"
        if reviews:
            for r in reviews:
                stars = "⭐️" * r["rating"]
                comment = r["comment"] if r["comment"] else "<em>Без комментариев</em>"
                html += f"""
                    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
                        <b>{r['name']}</b> {stars}
                        <p>{comment}</p>
                        <small>{r['created_at']}</small>
                    </div>
                """
        else:
            html += "<p>Пока нет отзывов. Будьте первым!"
            
        html += f"""
            <h3>Оставить отзыв</h3>
            <form method="post" action="/product/{product_id}/review">
                <div>
                    <label for="name">Ваше имя:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div>
                    <label for="rating">Ваша оценка (1 - 5):</label>
                    <input type="number" id="rating" name="rating" required>
                </div>
                <div>
                    <label for="comment">Комментарий:</label>
                    <textarea id="comment" name="comment" rows="4"></textarea>
                </div>
                <button type="submit">Отправить</button>
            </form>
        """
        html += "<p><a href='/catalog'>К списку товаров</a></p>"
        return html
    else:
        return "Товар не найден", 404
        
        
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
    html = render_flash()
    cart = get_cart(session)
    if not cart:
        html += "<h1>Корзина пуста</h1><a href='/catalog'>Вернуться в каталог</a>"
        return html
    product_ids = list(cart.keys())
    products = get_products_by_ids(product_ids)
    
    html += "<h1>Корзина</h1>"
    total = 0
    
    for product in products:
        product_id = product["id"]
        quantity = cart[product_id]
        subtotal = product["price"] * quantity
        total += subtotal
        
        html += f"""
        <div>
                <b>{product['name']}</b>
                x{quantity} = {subtotal} руб.
                <a href='/remove_from_cart/{product_id}'>Удалить</a>
        </div>
        """
    html += f"<h3>Итого: {total} руб.</h3>"
    html += "<a href='/checkout'>Оформить заказ</a><br>"
    html += "<a href='/catalog'>Продолжить покупки</a>"
    return html
    
    
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

    html = render_flash()
    html += "<h1>Оформление заказа</h1>"
    html += "<h3>Состав корзины</h3>"

    for product in products:
        qty = cart[product['id']]
        html += f"<div>{product['name']} * {qty} = {product['price'] * qty} руб.</div>"
    
    html += f"<p><b>Итого: {total} руб.</b></p>"

    html += """
        <form method='post' action='/checkout'>
            <div>
                <label for='customer_name'>Ваше имя:</label>
                <input type='text' id='customer_name' name='customer_name' required>
            </div>
            <div>
                <label for='customer_email'>Ваш email:</label>
                <input type='email' id='customer_email' name='customer_email' required>
            </div>
            <div>
                <label for='customer_phone'>Телефон:</label>
                <input type='text' id='customer_phone' name='customer_phone'>
            </div>
            <div>
                <label for='customer_address'>Адрес:</label>
                <textarea id='customer_address' name='customer_address' rows='3'></textarea>
            </div>
            <button type='submit'>Подтвердить заказ</button>
        </form>
    """
    html += "<a href='/cart'>Вернуться в корзину</a>"
    return html
    
    
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
    
    html = render_flash()
    html += f"<h1>Спасибо за заказ #{order_id[:8]}!</h1>"
    html += f"<p>Имя: {order['customer_name']}</p>"
    html += f"<p>Email: {order['customer_email']}"
    if order['customer_phone']:
        html += f"<p>Телефон: {order['customer_phone']}</p>"
    if order['customer_address']:
        html += f"<p>Адрес: {order['customer_address']}</p>"
    html += "<h3>Состав заказа:</h3>"
    
    for product_id, item in order['items'].items():
        html += f"<div>{item['name']} x{item['quantity']} = {item['price']*item['quantity']} руб.</div>"
    html += f"<p><b>Итого: {order['total']} руб.</b></p>"
    html += "<a href='/catalog'>Вернуться в каталог</a>"
    return html
    
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)