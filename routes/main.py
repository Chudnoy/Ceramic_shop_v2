from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from db import get_all_products, get_all_categories, get_category_by_slug, get_product_with_category, get_reviews_by_product, product_exists, get_product_by_id, add_review_db, create_order, get_order_by_id
from services.cart_service import get_cart, add_to_cart_serv, remove_from_cart_serv, clear_cart, build_cart_summary, get_cart_count, remove_unavailable_items
from services.order_service import process_checkout_form, build_order_items
from services.product_service import PRODUCT_STATUSES
from validation import validate_review
import uuid

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    """
Показывает главную страницу сайта.

Рендерит шаблон index.html без дополнительной бизнес-логики.
"""
    return render_template("index.html")


@main_bp.route("/catalog")
def catalog():
    """
Показывает клиентский каталог товаров.

Считывает параметры категории, сортировки и поиска из query string. Получает
товары через get_all_products без include_hidden, поэтому скрытые товары не
показываются клиентам. Проверяет существование выбранной категории и передаёт
товары, категории, текущие фильтры и статусы товаров в шаблон каталога.
"""
    category_slug = request.args.get('category')
    sort_by = request.args.get("sort_by", "name")
    order = request.args.get("order", "ASC").upper()
    search_query = request.args.get("q", "").strip()
    
    products = get_all_products(category_slug, sort_by, order, search_query)
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
                           category_slug=category_slug,
                           search_query=search_query, product_statuses=PRODUCT_STATUSES)
                           
                           
@main_bp.route('/product/<product_id>')
def product_page(product_id):
    """
Показывает страницу отдельного товара.

Загружает товар вместе с категорией и отзывами. Если товар не найден или имеет
статус "hidden", перенаправляет пользователя в каталог с сообщением об ошибке.
Для доступных к просмотру товаров передаёт данные товара, отзывы и словарь
статусов в шаблон страницы товара.
"""
    product = get_product_with_category(product_id)
    
    if not product:
        flash("Товар не найден", "error")
        return redirect(url_for("main.catalog"))
        
    if product["status"] == "hidden":
        flash("Товар не найден", "error")
        return redirect(url_for("main.catalog"))
        
    reviews = get_reviews_by_product(product_id)
    return render_template("product_page.html", product=product, reviews=reviews, product_statuses=PRODUCT_STATUSES)
    
    
@main_bp.route("/add_to_cart/<product_id>", methods=["POST"])
def add_to_cart_route(product_id):
    """
Обрабатывает добавление товара в корзину.

Проверяет количество из формы, существование товара и его статус. Добавлять в
корзину можно только товары со статусом "available". Поддерживает обычный POST
с redirect и AJAX-запросы с JSON-ответом, чтобы корзина могла обновляться без
перезагрузки страницы.
"""
    quantity_str = request.form.get("quantity", "1")
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        quantity = int(quantity_str)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        if is_ajax:
            return jsonify({
            "success": False,
            "message": "Количество должно быть положительным числом"}), 400
            
        return "Количество должно быть положительным числом", 400
        
    product = get_product_by_id(product_id)
        
    if not product:
        if is_ajax:
            return jsonify({
            "success": False,
            "message": "Товар не найден"
            }), 404
        
        flash("Товар не найден", "error")
        return redirect(url_for("main.catalog"))
        
    if product["status"] != "available":
        unavailable_messages = {
        "reserved": "Этот товар уже зарезервирован",
        "sold": "Этот товар уже продан",
        "hidden": "Товар не найден"
        }
        message = unavailable_messages.get(product["status"], "Этот товар сейчас недоступен для покупки")
        if is_ajax:
            return jsonify({
            "success": False,
            "message": message
            }), 409
            
        flash("Этот товар сейчас недоступен для покупки", "error")
        return redirect(url_for("main.catalog"))
        
    new_qty = add_to_cart_serv(session, product_id, quantity)
    cart_count = get_cart_count(session)

    if is_ajax:
        return jsonify({
            'success': True,
            'message': 'Товар добавлен в корзину',
            'cart_count': cart_count
        })
    
    flash(f"Товар «{product['name']}» добавлен в корзину (количество: {new_qty})", "success")
    return redirect(url_for("main.catalog"))
    
    
@main_bp.route("/cart")
def show_cart():
    """
Показывает страницу корзины.

Получает подробную сводку корзины через build_cart_summary, включая список товаров,
итоговую сумму только по доступным товарам и флаг наличия недоступных товаров.
Передаёт эти данные в шаблон корзины вместе со словарём статусов товаров.
"""
    cart_summary = build_cart_summary(session)
        
    return render_template("cart.html",
    products=cart_summary['products'],
    total=cart_summary['total'],
    cart=cart_summary['cart'],
    has_unavailable_items = cart_summary["has_unavailable_items"], product_statuses=PRODUCT_STATUSES)
    

@main_bp.route("/cart/remove_unavailable", methods=["POST"])
def remove_unavailable_route():
    """
Обрабатывает удаление недоступных товаров из корзины.

Вызывает cart_service.remove_unavailable_items, показывает пользователю сообщение
о результате операции и возвращает его на страницу корзины.
"""
    removed = remove_unavailable_items(session)
    
    if removed:
        flash("Недоступные товары удалены", "success")
    else:
        flash("Нет недоступных товаров", "error")
    
    return redirect(url_for("main.show_cart"))
    
    
@main_bp.route("/remove_from_cart/<product_id>", methods=['POST'])
def remove_from_cart_route(product_id):
    """
Обрабатывает удаление товара из корзины.

Удаляет товар из session-корзины через cart_service и заново собирает сводку
корзины. Поддерживает как обычный POST с redirect, так и AJAX-ответ с обновлённым
количеством товаров и итоговой суммой.
"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    removed = remove_from_cart_serv(session, product_id)

    cart_summary = build_cart_summary(session)

    if is_ajax:
        if removed:
            return jsonify({
                'success': True,
                'message': 'Товар удалён из корзины',
                'cart_count': cart_summary['cart_count'],
                'total': cart_summary['total']
            })
        return jsonify({
            'success': False,
            'message': 'Товар не найден в корзине',
            'cart_count': cart_summary["cart_count"],
            'total': cart_summary["total"]
        }), 404

    if removed:
        flash("Товар удалён из корзины", "info")
    else:
        flash("Товар не найден в корзине", "error")
    return redirect(url_for("main.show_cart"))


@main_bp.route('/cart/clear_cart', methods=['POST'])
def clear_cart_route():
    """
    Очищает корзину пользователя.

    Если в корзине есть товары, удаляет все позиции из session["cart"].
    После действия возвращает пользователя на страницу корзины.
    """
    
    if get_cart_count(session) > 0:
        clear_cart(session)
        flash('Корзина очищена', 'success')
    else:
        flash('В корзине нет товаров', 'error')
        
    return redirect(url_for('main.show_cart'))
    
    
@main_bp.route("/product/<product_id>/review", methods=["POST"])
def add_review(product_id):
    """
Обрабатывает добавление отзыва к товару.

Проверяет существование товара, получает имя, оценку и комментарий из формы,
валидирует данные через validate_review и сохраняет отзыв в базу. После успешного
добавления возвращает пользователя на страницу товара.
"""
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
    """
Показывает форму оформления заказа.

Собирает актуальную сводку корзины и пропускает к оформлению только если в корзине
есть товары, доступные для заказа. Недоступные товары не передаются в checkout.
Если часть товаров стала недоступна, показывает предупреждение, что они не будут
включены в заказ.
"""
    cart_summary = build_cart_summary(session)
    available_products = cart_summary["available_products"]

    if not cart_summary['cart']:
        flash("Корзина пуста", "error")
        return redirect(url_for("main.catalog"))
        
    if not available_products:
        flash("В корзине нет товаров, доступных для оформления", "error")
        return redirect(url_for("main.show_cart"))
        
    if cart_summary["has_unavailable_items"]:
        flash("Некоторые товары больше недоступны и не будут включены в заказ", "info")

    return render_template("checkout.html", products=available_products, total=cart_summary['total'], cart=cart_summary['cart'])
    
    
@main_bp.route("/checkout", methods=["POST"])
def checkout_process():
    """
Обрабатывает отправку формы оформления заказа.

Повторно собирает актуальную сводку корзины перед созданием заказа, чтобы не
оформить товары, которые стали недоступны после открытия страницы checkout.
Валидирует данные покупателя, формирует состав заказа только из доступных товаров,
создаёт заказ в базе данных, очищает корзину и перенаправляет на страницу успеха.
"""
    cart_summary = build_cart_summary(session)
    cart = cart_summary['cart']
    available_products = cart_summary["available_products"]
    
    if not cart:
        flash("Корзина пуста", "error")
        return redirect(url_for("main.catalog"))
    
    if not available_products:
        flash("В корзине нет товаров, доступных для оформления", "error")
        return redirect(url_for("main.show_cart"))
    
    is_valid, error_message, data = process_checkout_form(request.form)
    
    if not is_valid:
        flash(error_message, "error")
        return redirect(url_for("main.checkout_form"))
        
    items_dict, total = build_order_items(cart, available_products)
    
    order_id = str(uuid.uuid4())
    
    create_order(order_id, data["customer_name"], data["customer_email"], data["customer_phone"], data["customer_address"], items_dict, total)
    
    clear_cart(session)
    
    flash(f"Заказ {order_id[:8]} оформлен!", "success")
    
    return redirect(url_for("main.order_success", order_id=order_id))
    
    
@main_bp.route("/order_success/<order_id>")
def order_success(order_id):
    """
Показывает страницу успешного оформления заказа.

Ищет заказ по order_id. Если заказ не найден, возвращает пользователя в каталог.
Если найден, передаёт заказ и его товары в шаблон страницы успешного оформления.
"""
    order = get_order_by_id(order_id)
    
    if not order:
        flash("Заказ не найден", "error")
        return redirect(url_for("main.catalog"))
    
    order_items = order.get('items', {})
    
    return render_template("order_success.html", order=order, order_id=order_id, order_items=order_items)