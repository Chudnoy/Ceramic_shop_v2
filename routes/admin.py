from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from db import (get_all_products,
                get_all_orders,
                delete_product,
                update_product,
                get_product_by_id,
                get_all_categories, 
                create_product,
                delete_order,
                get_order_by_id,
                update_order,
                update_order_status,
                get_category_by_slug,
                get_admin_stats,
                create_category,
                delete_category,
                update_category,
                get_all_categories_with_product_count)
from services.product_service import process_product_form, PRODUCT_STATUSES
from services.image_service import save_image, delete_image
from services.order_service import process_order_form, ORDER_STATUSES
from services.category_service import process_category_form
from werkzeug.security import generate_password_hash, check_password_hash
import os
admin_bp = Blueprint("admin", __name__)

ADMIN_LOGIN = os.environ.get('ADMIN_LOGIN', 'admin')
ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH', '')


@admin_bp.before_request
def require_admin_login():
    """
Проверяет доступ к админским маршрутам перед каждым запросом.

Разрешает открывать страницу логина без авторизации. Для остальных admin routes
проверяет наличие session["is_admin"]. Если пользователь не авторизован как админ,
показывает flash-сообщение и перенаправляет на страницу входа.
"""
    allowed_endpoints = {
        'admin.login'
    }

    if request.endpoint in allowed_endpoints:
        return
    
    if session.get('is_admin'):
        return
    
    flash('Сначала войдите в админку', 'error')
    return redirect(url_for('admin.login'))


@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    """
Обрабатывает вход в админку.

При GET-запросе показывает форму входа. При POST-запросе проверяет логин и пароль
по значениям из переменных окружения. Если данные верны, сохраняет признак
администратора в session и перенаправляет на главную страницу админки.
"""
    if request.method == 'POST':
        login_value = request.form.get('login', '').strip()
        password = request.form.get('password', '')

        if login_value == ADMIN_LOGIN and ADMIN_PASSWORD_HASH and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session.permanent = True
            session['is_admin'] = True
            flash('Вы вошли в админку', 'success')
            return redirect(url_for('admin.admin'))
        
        flash('Неверный логин или пароль', 'error')
    return render_template('admin/login.html')


@admin_bp.route('/admin/logout', methods=['POST'])
def logout():
    """
Выводит пользователя из админки.

Удаляет флаг is_admin из session, показывает flash-сообщение и перенаправляет
пользователя на страницу входа в админку.
"""
    session.pop('is_admin', None)
    flash('Вы вышли из админки', 'info')
    return redirect(url_for('admin.login'))


@admin_bp.route("/admin")
def admin():
    """
Показывает главную страницу админки.

Получает статистику через get_admin_stats и передаёт её в шаблон admin/index.html.
Используется как стартовая панель управления магазином.
"""
    stats = get_admin_stats()
    return render_template("admin/index.html", stats=stats)
    
    
@admin_bp.route("/admin/products")
def admin_products():
    """
Показывает список товаров в админке с фильтрацией, поиском и сортировкой.

Считывает параметры category, sort_by, order и q из query string. Проверяет
существование выбранной категории, получает список товаров с include_hidden=True,
чтобы админ видел все товары, включая скрытые, и передаёт данные в шаблон.
"""
    category_slug = request.args.get('category')
    sort_by = request.args.get('sort_by', 'name')
    order = request.args.get('order', 'ASC').upper()
    search_query = request.args.get('q', '').strip()

    categories = get_all_categories()

    current_category = None

    if category_slug:
        current_category = get_category_by_slug(category_slug)
        if not current_category:
            flash('Категория не найдена', 'error')
            return redirect(url_for('admin.admin_products'))
        
    products = get_all_products(category_slug, sort_by, order, search_query, include_hidden=True)
        
    return render_template("admin/products.html",
                           products=products,
                           categories=categories,
                           category_slug=category_slug,
                           current_category=current_category,
                           current_sort=sort_by,
                           current_order=order,
                           search_query=search_query,
                           product_statuses=PRODUCT_STATUSES)


@admin_bp.route("/admin/orders")
def admin_orders():
    """
Показывает список заказов в админке.

Считывает поисковый запрос и выбранный статус из query string, получает подходящие
заказы из базы и передаёт их в шаблон вместе со словарём доступных статусов заказа.
"""
    search_query = request.args.get('q', '').strip()
    status = request.args.get('status', '')
    orders = get_all_orders(search_query, status)
    return render_template("admin/orders.html",
                           orders=orders,
                           order_statuses=ORDER_STATUSES,
                           search_query=search_query,
                           current_status=status)


@admin_bp.route("/admin/orders/order_details/<order_id>")
def order_details(order_id):
    """
Показывает подробную страницу одного заказа.

Ищет заказ по order_id. Если заказ не найден, показывает ошибку и возвращает
пользователя к списку заказов. Если найден, передаёт заказ и доступные статусы
в шаблон деталей заказа.
"""
    order = get_order_by_id(order_id)
    if not order:
        flash('Заказ не найден', 'error')
        return redirect(url_for('admin.admin_orders'))
    return render_template("admin/order_details.html", order=order, order_statuses=ORDER_STATUSES)
    
    
@admin_bp.route("/admin/orders/delete/<order_id>", methods=["POST"])
def delete_order_route(order_id):
    """
Обрабатывает удаление заказа из админки.

Перед удалением проверяет, существует ли заказ. Если заказ найден, удаляет его
из базы данных, показывает flash-сообщение и возвращает пользователя к списку
заказов.
"""
    order = get_order_by_id(order_id)
    if not order:
        flash('Заказ не найден', 'error')
        return redirect(url_for('admin.admin_orders'))
    delete_order(order_id)
    flash("Заказ удалён", "info")
    return redirect(url_for("admin.admin_orders"))


@admin_bp.route("/admin/orders/<order_id>/status", methods=["POST"])
def update_order_status_route(order_id):
    """
Обрабатывает быстрое изменение статуса заказа.

Получает новый статус из формы, проверяет существование заказа и допустимость
статуса. Если всё корректно, обновляет статус заказа и возвращает пользователя
к списку заказов.
"""
    status = request.form.get("status", "new")
    order = get_order_by_id(order_id)
    if not order:
        flash('Заказ не найден', 'error')
        return redirect(url_for('admin.admin_orders'))
    if status not in ORDER_STATUSES:
        flash("Некорректный статус заказа", "error")
        return redirect(url_for("admin.admin_orders"))

    update_order_status(order_id, status)

    flash("Статус заказа обновлён", "success")
    return redirect(url_for("admin.admin_orders"))
    
    
@admin_bp.route("/admin/orders/edit/<order_id>", methods=["GET", "POST"])
def edit_order(order_id):
    """
Обрабатывает просмотр и редактирование заказа в админке.

При GET-запросе показывает форму редактирования заказа. При POST-запросе
проверяет данные формы через process_order_form, пересчитывает состав и сумму
заказа, обновляет заказ в базе и возвращает пользователя к списку заказов.
"""
    order = get_order_by_id(order_id)
    if not order:
        flash('Заказ не найден', 'error')
        return redirect(url_for('admin.admin_orders'))
    if request.method == "POST":
        is_valid, error_message, data = process_order_form(request.form, order['items'])

        if not is_valid:
            flash(error_message, 'error')
            return redirect(url_for('admin.edit_order', order_id=order_id))
        
        update_order(order_id, data['name'], data['email'], data['phone'], data['address'], data['items'], data['total'], data['status'])
        flash("Заказ обновлён", "success")
        return redirect(url_for("admin.admin_orders"))
    
    return render_template("admin/order_form.html", order=order, order_statuses=ORDER_STATUSES)

    
@admin_bp.route("/admin/products/delete/<product_id>", methods=['POST'])
def delete_product_route(product_id):
    """
Обрабатывает удаление товара из админки.

Если товар найден, сначала удаляет связанное изображение через image_service,
затем удаляет запись товара из базы данных. После операции возвращает пользователя
к списку товаров.
"""
    product = get_product_by_id(product_id)
    if product:
        delete_image(product["img"])
        delete_product(product_id)
    flash("Товар удалён", "info")
    return redirect(url_for("admin.admin_products"))
    
    
@admin_bp.route("/admin/products/edit/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    """
Обрабатывает редактирование товара в админке.

При GET-запросе показывает форму с текущими данными товара. При POST-запросе
валидирует данные формы, сохраняет новое изображение при его наличии, сохраняет
старое изображение при отсутствии нового файла и обновляет товар в базе данных,
включая его статус.
"""
    product = get_product_by_id(product_id)

    if not product:
        flash('Товар не найден', 'error')
        return redirect(url_for('admin.admin_products'))
    if request.method == "POST":
        is_valid, error_message, data = process_product_form(request.form)
        
        if not is_valid:
            flash(error_message, "error")
            return redirect(url_for("admin.edit_product", product_id=product_id))
        
        file = request.files.get('img')
        image_success, image_error, image_path = save_image(file)
        
        if not image_success:
            flash(image_error, 'error')
            return redirect(url_for('admin.edit_product', product_id=product_id))

        if image_path:
            data['img'] = image_path
        else:
            data['img'] = product['img']
        
        update_product(product_id, data["name"], data["price"], data["description"], data["img"], data["category_id"], data["status"])
        
        flash("Товар обновлён", "success")
        return redirect(url_for("admin.admin_products"))
        
    categories = get_all_categories()
    return render_template("admin/product_form.html",
                           product=product,
                           categories=categories,
                           title="Редактирование товара",
                           submit_text="Сохранить",
                           product_statuses=PRODUCT_STATUSES)
    
    
@admin_bp.route("/admin/products/new", methods=["GET", "POST"])
def new_product():
    """
Обрабатывает создание нового товара в админке.

При GET-запросе показывает пустую форму создания товара со статусом "available"
по умолчанию. При POST-запросе валидирует данные формы, сохраняет изображение,
создаёт новый товар в базе данных и возвращает пользователя к списку товаров.
"""
    categories = get_all_categories()
    
    if request.method == "POST":
        is_valid, error_message, data = process_product_form(request.form)
        
        if not is_valid:
            flash(error_message, "error")
            return redirect(url_for("admin.new_product"))
        
        file = request.files.get('img')
        image_success, image_error, image_path = save_image(file)
        
        if not image_success:
            flash(image_error, 'error')
            return redirect(url_for('admin.new_product'))

        data['img'] = image_path
            
        create_product(data["name"], data["price"], data["description"], data["img"], data["category_id"], data["status"])
        
        flash("Товар создан", "success")
        return redirect(url_for("admin.admin_products"))
        
    empty_product = {"name": "", "description": "", "price": "", "category_id": None, "img": "", "status": "available"}
    
    return render_template("admin/product_form.html",
                           product=empty_product,
                           categories=categories,
                           title="Новый товар",
                           submit_text="Создать",
                           product_statuses=PRODUCT_STATUSES)


@admin_bp.route('/admin/categories')
def admin_categories():
    """
	Показывает список категорий в админке.

	Загружает категории из базы данных и передаёт их в шаблон
	для отображения администратору.
	"""
    categories = get_all_categories_with_product_count()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/admin/categories/new', methods=['GET', 'POST'])
def new_category_route():
    """
	Обрабатывает создание новой категории в админке.

	При GET-запросе показывает пустую форму создания категории.
	При POST-запросе обрабатывает данные формы, валидирует название, slug
	и описание, проверяет уникальность slug, создаёт категорию в базе данных
	и возвращает администратора к списку категорий.
	"""
    if request.method == 'POST':
        is_valid, error_message, data = process_category_form(request.form)
        
        if not is_valid:
            flash(error_message, 'error')
            return redirect(url_for('admin.new_category_route'))
        
        category_exists = get_category_by_slug(data['slug']) is not None

        if category_exists:
            flash('Категория с таким slug уже существует', 'error')
            return redirect(url_for('admin.new_category_route'))
        
        create_category(data['name'], data['slug'], data['description'])
        flash('Категория создана', 'success')
        return redirect(url_for('admin.admin_categories'))

    empty_category = {'name': '', 'slug': '', 'description': ''}

    return render_template('admin/category_form.html',
                           category=empty_category,
                           title='Создать категорию',
                           submit_text='Создать')


@admin_bp.route('/admin/categories/edit/<slug>', methods=['GET', 'POST'])
def edit_category_route(slug):
    """
	Обрабатывает редактирование категории в админке.

	Находит категорию по текущему slug. Если категория не найдена,
	перенаправляет администратора к списку категорий.

	При GET-запросе показывает форму редактирования с текущими данными категории.
	При POST-запросе валидирует данные формы, проверяет уникальность нового slug
	при его изменении, обновляет категорию в базе данных и возвращает
	администратора к списку категорий.
	"""
    category = get_category_by_slug(slug)

    if not category:
        flash('Категория не найдена', 'error')
        return redirect(url_for('admin.admin_categories'))
    
    if request.method == 'POST':
        is_valid, error_message, data = process_category_form(request.form)

        if not is_valid:
            flash(error_message, 'error')
            return redirect(url_for('admin.edit_category_route', slug=slug))
        
        if data['slug'] != category['slug']:
            category_exists = get_category_by_slug(data['slug']) is not None
            if category_exists:
                flash('Категория с таким slug уже существует', 'error')
                return redirect(url_for('admin.edit_category_route', slug=slug))
        
        update_category(data['name'], data['slug'], data['description'], slug)

        flash('Категория обновлена', 'success')
        return redirect(url_for('admin.admin_categories'))
    
    return render_template('admin/category_form.html',
                           category=category,
                           title='Редактирование категории',
                           submit_text='Сохранить')


@admin_bp.route('/admin/categories/delete/<slug>', methods=['POST'])
def delete_category_route(slug):
    """
	Обрабатывает удаление категории из админки.

	Находит категорию по slug и пытается удалить её из базы данных.
	Категория удаляется только в том случае, если к ней не привязаны товары.
	После операции показывает администратору сообщение о результате и возвращает
	его к списку категорий.
	"""
    category = get_category_by_slug(slug)
    
    if category:
        if delete_category(category['id']):
            flash('Категория удалена', 'success')
        else:
            flash('В категории ещё есть товары', 'error')
    else:
        flash('Категория не найдена', 'error')
            
    return redirect(url_for('admin.admin_categories'))