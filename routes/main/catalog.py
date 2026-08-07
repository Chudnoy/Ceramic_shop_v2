from flask import flash, redirect, render_template, request, url_for

from database.categories import get_all_categories, get_category_by_slug
from database.products import (
    get_all_products,
    get_product_with_category,
)
from database.tags import get_tag_by_slug, get_tags_for_product
from services.product_service import PRODUCT_STATUSES

from . import main_bp


@main_bp.route("/")
def index():
    products = get_all_products(
        is_archived=False, only_visible=True, only_featured=True
    )
    return render_template("index.html", products=products)


@main_bp.route("/catalog")
def catalog():
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

    products = get_all_products(
        category_slug=category_slug,
        sort_by=sort_by,
        order=order,
        search_query=search_query,
        tag_slug=tag_slug,
    )

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
        product_statuses=PRODUCT_STATUSES,
    )


@main_bp.route("/product/<product_id>")
def product_page(product_id):
    product = get_product_with_category(product_id)

    if not product:
        flash("Работа не найдена", "error")
        return redirect(url_for("main.catalog"))

    if product["is_visible"] != 1 or product["is_archived"] == 1:
        flash("Работа не найдена", "error")
        return redirect(url_for("main.catalog"))

    tags = get_tags_for_product(product_id)

    return render_template(
        "product_page.html",
        tags=tags,
        product=product,
        product_statuses=PRODUCT_STATUSES,
    )
