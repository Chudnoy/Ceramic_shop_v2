from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_all_products, get_all_categories, get_category_by_slug

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
            return redirect(url_for('catalog'))
    
    return render_template("catalog.html",
                           products=products,
                           categories=categories,
                           current_category=current_category,
                           current_sort=sort_by,
                           current_order=order,
                           category_slug=category_slug)