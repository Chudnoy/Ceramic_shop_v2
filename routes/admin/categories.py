from flask import flash, redirect, render_template, request, url_for

from database.categories import (
    delete_category,
    get_all_categories_with_product_count,
    get_category_by_slug,
)
from services.category_service import (
    create_category_from_form,
    update_category_from_form,
)

from . import admin_bp


@admin_bp.route("/admin/categories")
def admin_categories():
    """
    Показывает список категорий в админке.

    Загружает категории из базы данных и передаёт их в шаблон
    для отображения администратору.
    """
    categories = get_all_categories_with_product_count()
    return render_template("admin/categories.html", categories=categories)


@admin_bp.route("/admin/categories/new", methods=["GET", "POST"])
def new_category_route():
    if request.method == "POST":
        is_created, error_message = create_category_from_form(request.form)

        if not is_created:
            flash(error_message, "error")
            return redirect(url_for("admin.new_category_route"))

        flash("Категория создана", "success")
        return redirect(url_for("admin.admin_categories"))

    empty_category = {"name": "", "slug": "", "description": ""}

    return render_template(
        "admin/category_form.html",
        category=empty_category,
        title="Создать категорию",
        submit_text="Создать",
    )


@admin_bp.route("/admin/categories/edit/<slug>", methods=["GET", "POST"])
def edit_category_route(slug):
    category = get_category_by_slug(slug)

    if not category:
        flash("Категория не найдена", "error")
        return redirect(url_for("admin.admin_categories"))

    if request.method == "POST":
        is_updated, error_message = update_category_from_form(request.form, category)
        if not is_updated:
            flash(error_message, "error")
            return redirect(url_for("admin.edit_category_route", slug=slug))

        flash("Категория обновлена", "success")
        return redirect(url_for("admin.admin_categories"))

    return render_template(
        "admin/category_form.html",
        category=category,
        title="Редактирование категории",
        submit_text="Сохранить",
    )


@admin_bp.route("/admin/categories/delete/<slug>", methods=["POST"])
def delete_category_route(slug):
    category = get_category_by_slug(slug)

    if not category:
        flash("Категория не найдена", "error")
        return redirect(url_for("admin.admin_categories"))

    is_deleted, error_message = delete_category(category["id"])

    if not is_deleted:
        flash(error_message, "error")
    else:
        flash("Категория удалена", "success")

    return redirect(url_for("admin.admin_categories"))
