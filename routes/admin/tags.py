from flask import flash, redirect, render_template, request, url_for

from database.products import get_products_by_tag_slug
from database.tags import (
    create_tag,
    delete_tag_by_id,
    get_all_tags,
    get_product_count_by_tag_id,
    get_tag_by_id,
    get_tag_by_slug,
    get_tags_with_product_count,
    update_tag,
)
from services.tag_service import process_tag_form

from . import admin_bp


@admin_bp.route('/admin/tags')
def admin_tags_route():
    tags = get_tags_with_product_count()
    
    return render_template('admin/tags.html', tags=tags)
    
    
@admin_bp.route('/admin/tags/new', methods=['GET', 'POST'])
def new_tag_route():
    
    if request.method == 'POST':
        is_valid_tag, error_message, tag_data = process_tag_form(request.form)
        
        if not is_valid_tag:
            flash(error_message, 'error')
            return redirect(url_for('admin.new_tag_route'))
        
        tags = get_all_tags()
        
        existing_names = {tag['name'] for tag in tags}
        existing_slugs = {tag['slug'] for tag in tags}
        
        if tag_data['tag_name'] in existing_names:
            flash('Тег с таким названием уже существует', 'error')
            return redirect(url_for('admin.new_tag_route'))
        
        if tag_data['tag_slug'] in existing_slugs:
            flash('Тег с таким slug уже существует', 'error')
            return redirect(url_for('admin.new_tag_route'))

        create_tag(tag_data['tag_name'], tag_data['tag_slug'])

        flash(f"Тег «{tag_data['tag_name']}» добавлен", 'success')
        return redirect(url_for('admin.admin_tags_route'))
    
    empty_tag = {'id': '', 'name': '', 'slug': ''}
    
    return render_template('admin/tag_form.html', title='Добавление тега', submit_text='Добавить', tag=empty_tag)


@admin_bp.route('/admin/tags/edit/<tag_slug>', methods=['GET', 'POST'])
def edit_tag_route(tag_slug):
    tag = get_tag_by_slug(tag_slug)
    
    if not tag:
        flash('Тег не найден', 'error')
        return redirect(url_for('admin.admin_tags_route'))
    
    if request.method == 'POST':
        is_valid_tag, error_message, tag_data = process_tag_form(request.form)
        
        if not is_valid_tag:
            flash(error_message, 'error')
            return redirect(url_for('admin.edit_tag_route', tag_slug=tag_slug))
        
        tags = get_all_tags()
        
        existing_names = {tag['name'] for tag in tags}
        existing_slugs = {tag['slug'] for tag in tags}
        
        if (
            tag_data['tag_name'] != tag['name']
            and tag_data['tag_name'] in existing_names
        ):
            flash('Тег с таким названием уже существует', 'error')
            return redirect(
                url_for('admin.edit_tag_route', tag_slug=tag_slug)
            )
        
        if (
            tag_data['tag_slug'] != tag['slug']
            and tag_data['tag_slug'] in existing_slugs
        ):
            flash('Тег с таким slug уже существует', 'error')
            return redirect(
                url_for('admin.edit_tag_route', tag_slug=tag_slug)
            )

        update_tag(tag_data['tag_name'], tag_data['tag_slug'], tag['id'])

        flash(f"Тег «{tag_data['tag_name']}» изменён", 'success')
        return redirect(url_for('admin.admin_tags_route'))
    
    return render_template('admin/tag_form.html', title=f"Изменение тега «{tag['name']}»", submit_text='Сохранить', tag=tag)
    
    
@admin_bp.route('/admin/tags/delete/<tag_id>', methods=['POST'])
def delete_tag_route(tag_id):
    
    tag = get_tag_by_id(tag_id)
    
    if not tag:
        flash('Тег не найден', 'error')
        return redirect(url_for('admin.admin_tags_route'))

    if get_product_count_by_tag_id(tag_id):
        flash("Этот тег используется в работах и пока не может быть удалён", 'error')
        return redirect(url_for('admin.admin_tags_route'))
    
    tag_name = tag['name']
    delete_tag_by_id(tag_id)
    
    flash(f'Тег {tag_name} удалён', 'success')
    return redirect(url_for('admin.admin_tags_route'))
    
    
@admin_bp.route("/admin/tags/tag_detail/<tag_slug>")
def tag_details(tag_slug):
    tag = get_tag_by_slug(tag_slug)

    if not tag:
        flash("Тег не найден", "error")
        return redirect(url_for("admin.admin_tags_route"))

    products = get_products_by_tag_slug(tag_slug, only_visible=False)

    return render_template("admin/tag_details.html", tag=tag, products=products)