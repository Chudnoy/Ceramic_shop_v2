from flask import Blueprint, render_template, redirect, url_for, flash, request
from db import (get_all_products, delete_product, update_product, get_product_by_id, get_all_categories, create_product)
from validation import validate_product
from services.product_service import process_product_form
from services.image_service import save_uploaded_image
admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin")
def admin():
    return render_template("admin/index.html")
    
    
@admin_bp.route("/admin/products")
def admin_products():
    products = get_all_products()
    return render_template("admin/products.html", products=products)
    
    
@admin_bp.route("/admin/products/delete/<product_id>")
def delete_product_route(product_id):
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
        new_img = save_uploaded_image(file)

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
        data['img'] = save_uploaded_image(file)
            
        create_product(data["name"], data["price"], data["description"], data["img"], data["category_id"])
        
        flash("Товар создан", "success")
        return redirect(url_for("admin.admin_products"))
        
    empty_product = {"name": "", "description": "", "price": "", "category_id": None, "img": ""}
    
    return render_template("admin/product_form.html", product=empty_product, categories=categories, title="Новый товар", submit_text="Создать")