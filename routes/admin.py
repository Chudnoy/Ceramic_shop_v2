from flask import Blueprint, render_template, redirect, url_for, flash, request
from db import get_all_products, delete_product, update_product, get_product_by_id, get_all_categories
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
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", 0)
        category_id = request.form.get("category_id")
        
        update_product(product_id, name, description, price, category_id)
        flash("Товар обновлён", "success")
        return redirect(url_for("admin.admin_products"))
    product = get_product_by_id(product_id)
    categories = get_all_categories()
    return render_template("admin/edit_product.html", product=product, categories=categories)