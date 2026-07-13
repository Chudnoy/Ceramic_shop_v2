from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database.categories import (
    get_all_categories,
    get_category_by_slug,
)

from database.orders import (
    create_order,
    get_order_by_id,
)

from database.products import (
    get_all_products,
    get_product_by_id,
    get_product_with_category,
    get_products_by_tag_slug,
    product_exists,
)

from database.reviews import (
    add_review_db,
    get_reviews_by_product,
)

from database.tags import (
    get_tag_by_slug,
    get_tags_for_product,
)
from services.cart_service import get_cart, add_to_cart_serv, remove_from_cart_serv, clear_cart, build_cart_summary, get_cart_count, remove_unavailable_items
from services.order_service import process_checkout_form, build_order_items
from services.product_service import PRODUCT_STATUSES, get_product_cart_unavailable_reason
from validation import validate_review
import uuid

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    """
Показывает главную страницу сайта.

Рендерит шаблон index.html без дополнительной бизнес-логики.
"""
    products = get_all_products(is_archived=False, only_visible=True, only_featured=True)
    return render_template("index.html", products=products)


@main_bp.route("/catalog")
def catalog():
    """
    Показывает клиентский каталог работ.

    Считывает параметры категории, тега, сортировки и поиска из query string.
    Если выбран тег, получает работы, связанные с этим тегом. Если тег не выбран,
    получает работы через get_all_products с учётом категории, поиска и сортировки.

    Скрытые работы не показываются клиентам. Проверяет существование выбранной
    категории и выбранного тега, затем передаёт работы, категории, текущие фильтры,
    тег и словарь статусов в шаблон каталога.
    """
    category_slug = request.args.get("category")
    sort_by = request.args.get("sort_by", "name")
    order = request.args.get("order", "ASC").upper()
    search_query = request.args.get("q", "").strip()
    tag_slug = request.args.get("tag", "")

    categories = get_all_categories()

    current_category = None
    if category_slug:
        current_category = get_category_by_slug(category_slug)
        if not current_category:
            flash("Категория не найдена", "error")
            return redirect(url_for("main.catalog"))

    tag = None
    if tag_slug:
        tag = get_tag_by_slug(tag_slug)
        if not tag:
            flash("Тег не найден", "error")
            return redirect(url_for("main.catalog"))

        products = get_products_by_tag_slug(tag_slug)
    else:
        products = get_all_products(category_slug, sort_by, order, search_query)

    return render_template(
        "catalog.html",
        products=products,
        tag=tag,
        categories=categories,
        current_category=current_category,
        current_sort=sort_by,
        current_order=order,
        current_tag=tag_slug,
        category_slug=category_slug,
        search_query=search_query,
        product_statuses=PRODUCT_STATUSES
    )
                           
                           
@main_bp.route('/product/<product_id>')
def product_page(product_id):
    """
Показывает страницу отдельной работы.

Загружает работу вместе с категорией, отзывами и тегами. Если работа не найдена
или скрыта с публичной части сайта, перенаправляет пользователя в каталог
с сообщением об ошибке.

Для доступных к просмотру работ передаёт данные работы, отзывы, теги и словарь
статусов в шаблон страницы работы.
"""
    product = get_product_with_category(product_id)
    
    if not product:
        flash("Работа не найдена", "error")
        return redirect(url_for("main.catalog"))
        
    if product["is_visible"] != 1 or product["is_archived"] == 1:
        flash("Работа не найдена", "error")
        return redirect(url_for("main.catalog"))
        
    reviews = get_reviews_by_product(product_id)
    tags = get_tags_for_product(product_id)
    
    return render_template("product_page.html", tags=tags, product=product, reviews=reviews, product_statuses=PRODUCT_STATUSES)
    
    
@main_bp.route("/add_to_cart/<product_id>", methods=["POST"])
def add_to_cart_route(product_id):
    """
Обрабатывает добавление работы в корзину.

Проверяет количество из формы, существование работы, публичную видимость,
возможность продажи и статус. Добавлять в корзину можно только опубликованные
работы, предназначенные для продажи и имеющие статус "available".

Поддерживает обычный POST с redirect и AJAX-запросы с JSON-ответом.
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
            "message": "Количество должно быть положительным числом",
            "cart_count": get_cart_count(session)
            }), 400
            
        flash("Количество должно быть положительным числом", "error")
        return redirect(url_for("main.product_page", product_id=product_id))
        
    product = get_product_by_id(product_id)
        
    unavailable_reason = get_product_cart_unavailable_reason(product)
    
    if unavailable_reason:
        if is_ajax:
            return jsonify({
            "success": False,
            "message": unavailable_reason,
            "cart_count": get_cart_count(session)
            }), 409
        
        flash(unavailable_reason, "error")
        
        if not product:
            return redirect(url_for("main.catalog"))
            
        return redirect(url_for("main.product_page", product_id=product_id))
        
    new_qty = add_to_cart_serv(session, product_id, quantity)
    cart_count = get_cart_count(session)

    if is_ajax:
        return jsonify({
            'success': True,
            'message': 'Работа добавлена в корзину',
            'cart_count': cart_count
        })
    
    flash(f"Работа «{product['name']}» добавлена в корзину (количество: {new_qty})", "success")
    return redirect(url_for("main.product_page", product_id=product_id))
    
    
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
        flash("Недоступные работы удалены", "success")
    else:
        flash("Нет недоступных работ", "error")
    
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
                'message': 'Работа удалена из корзины',
                'cart_count': cart_summary['cart_count'],
                'total': cart_summary['total']
            })
        return jsonify({
            'success': False,
            'message': 'Работа не найдена в корзине',
            'cart_count': cart_summary["cart_count"],
            'total': cart_summary["total"]
        }), 404

    if removed:
        flash("Работа удалена из корзины", "info")
    else:
        flash("Работа не найдена в корзине", "error")
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
        flash('В корзине нет работ', 'error')
        
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
        flash("Работа не найдена", "error")
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

Собирает актуальную сводку корзины через build_cart_summary().
К оформлению передаются только работы, которые сейчас доступны для покупки.
Если в корзине есть недоступные работы, пользователь получает предупреждение,
а эти работы не включаются в заказ.
"""
    cart_summary = build_cart_summary(session)
    available_products = cart_summary["available_products"]

    if not cart_summary['cart']:
        flash("Корзина пуста", "error")
        return redirect(url_for("main.catalog"))
        
    if not available_products:
        flash("В корзине нет работ, доступных для оформления", "error")
        return redirect(url_for("main.show_cart"))
        
    if cart_summary["has_unavailable_items"]:
        flash("Некоторые работы больше недоступны и не будут включены в заказ", "info")

    return render_template("checkout.html", products=available_products, total=cart_summary['total'], cart=cart_summary['cart'])
    
    
@main_bp.route("/checkout", methods=["POST"])
def checkout_process():
    """
Обрабатывает отправку формы оформления заказа.

Повторно собирает актуальную сводку корзины перед созданием заказа.
Заказ создаётся только из работ, которые на момент отправки формы доступны
для покупки. Недоступные работы из корзины в заказ не включаются.
"""
    cart_summary = build_cart_summary(session)
    cart = cart_summary['cart']
    available_products = cart_summary["available_products"]
    
    if not cart:
        flash("Корзина пуста", "error")
        return redirect(url_for("main.catalog"))
    
    if not available_products:
        flash("В корзине нет работ, доступных для оформления", "error")
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