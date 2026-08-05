from flask import flash, redirect, render_template, request, url_for

from database.categories import (
    create_category,
    delete_category,
    get_all_categories_with_product_count,
    get_category_by_slug,
    update_category,
)
from services.category_service import process_category_form

from . import admin_bp


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
    
    if not category:
        flash("Категория не найдена", "error")
        return redirect(url_for("admin.admin_categories"))
    
    if delete_category(category["id"]):
        flash("Категория удалена", "success")
    else:
        flash("Категорию нельзя удалить пока к ней привязаны работы", "error")
        
    return redirect(url_for("admin.admin_categories"))