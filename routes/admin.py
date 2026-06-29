from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from db import (get_all_products, get_all_orders, delete_product, update_product, get_product_by_id, get_all_categories, create_product, delete_order, get_order_by_id, update_order)
from validation import validate_product
from services.product_service import process_product_form
from services.image_service import save_image, delete_image
from services.order_service import process_order_form
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
admin_bp = Blueprint("admin", __name__)

ADMIN_LOGIN = os.environ.get('ADMIN_LOGIN', 'admin')
ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH', '')


@admin_bp.before_request
def require_admin_login():
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


@admin_bp.route('/admin/logout')
def logout():
    session.pop('is_admin', None)
    flash('Вы вышли из админки', 'info')
    return redirect(url_for('admin.login'))


@admin_bp.route("/admin")
def admin():
    return render_template("admin/index.html")
    
    
@admin_bp.route("/admin/products")
def admin_products():
    products = get_all_products()
    return render_template("admin/products.html", products=products)
    
    
@admin_bp.route("/admin/orders/order_details/<order_id>")
def order_details(order_id):
    order = get_order_by_id(order_id)
    if not order:
        flash('Заказ не найден', 'error')
        return redirect(url_for('admin.admin_orders'))
    return render_template("admin/order_details.html", order=order)


@admin_bp.route("/admin/orders")
def admin_orders():
    orders = get_all_orders()
    return render_template("admin/orders.html", orders=orders)
    
    
@admin_bp.route("/admin/orders/delete/<order_id>", methods=["POST"])
def delete_order_route(order_id):
    delete_order(order_id)
    flash("Заказ удалён", "info")
    return redirect(url_for("admin.admin_orders"))
    
    
@admin_bp.route("/admin/orders/edit/<order_id>", methods=["GET", "POST"])
def edit_order(order_id):
    order = get_order_by_id(order_id)
    if not order:
        flash('Заказ не найден', 'error')
        return redirect(url_for('admin.admin_orders'))
    if request.method == "POST":
        is_valid, error_message, data = process_order_form(request.form, order['items'])

        if not is_valid:
            flash(error_message, 'error')
            return redirect(url_for('admin.edit_order', order_id=order_id))
        
        update_order(order_id, data['name'], data['email'], data['phone'], data['address'], data['items'], data['total'])
        flash("Заказ обновлён", "success")
        return redirect(url_for("admin.admin_orders"))
    
    return render_template("admin/order_form.html", order=order)

    
@admin_bp.route("/admin/products/delete/<product_id>", methods=['POST'])
def delete_product_route(product_id):
    product = get_product_by_id(product_id)
    if product:
        delete_image(product["img"])
        delete_product(product_id)
    flash("Товар удалён", "info")
    return redirect(url_for("admin.admin_products"))
    
    
@admin_bp.route("/admin/products/edit/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    product = get_product_by_id(product_id)
    if request.method == "POST":
        is_valid, error_message, data = process_product_form(request.form)
        
        if not is_valid:
            flash(error_message, "error")
            return redirect(url_for("admin.edit_product", product_id=product_id))
        
        file = request.files.get('img')
        new_img = save_image(file)

        if new_img:
            data['img'] = new_img
        else:
            data['img'] = product['img']
        
        update_product(product_id, data["name"], data["price"], data["description"], data["img"], data["category_id"])
        
        flash("Товар обновлён", "success")
        return redirect(url_for("admin.admin_products"))
        
    categories = get_all_categories()
    return render_template("admin/product_form.html", product=product, categories=categories, title="Редактирование товара", submit_text="Сохранить")
    
    
@admin_bp.route("/admin/products/new", methods=["GET", "POST"])
def new_product():
    categories = get_all_categories()
    
    if request.method == "POST":
        is_valid, error_message, data = process_product_form(request.form)
        
        if not is_valid:
            flash(error_message, "error")
            return redirect(url_for("admin.new_product"))
        
        file = request.files.get('img')
        data['img'] = save_image(file)
            
        create_product(data["name"], data["price"], data["description"], data["img"], data["category_id"])
        
        flash("Товар создан", "success")
        return redirect(url_for("admin.admin_products"))
        
    empty_product = {"name": "", "description": "", "price": "", "category_id": None, "img": ""}
    
    return render_template("admin/product_form.html", product=empty_product, categories=categories, title="Новый товар", submit_text="Создать")