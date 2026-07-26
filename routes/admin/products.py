from flask import flash, redirect, render_template, request, url_for

from database.categories import (
    get_all_categories,
    get_category_by_slug
)
from database.products import (
    get_all_products,
    get_product_by_id,
    set_product_archived
)
from database.tags import (
    get_all_tags,
    get_tags_for_product
)
from services.product_service import (
    PRODUCT_STATUSES,
    process_product_form,
    process_product_state_form,
    process_product_tag_ids,
    create_product_with_tags,
    update_product_with_tags,
    delete_product_with_image,
    update_product_state_with_order_check
)

from . import admin_bp

@admin_bp.route("/admin/products")
def admin_products():
    """
Показывает список товаров в админке с фильтрацией, поиском и сортировкой.

Считывает параметры category, sort_by, order и q, query string и status. Проверяет
существование выбранной категории, получает список товаров с include_hidden=True,
чтобы админ видел все товары, включая скрытые, и передаёт данные в шаблон.
"""
    category_slug = request.args.get('category')
    sort_by = request.args.get('sort_by', 'name')
    order = request.args.get('order', 'ASC').upper()
    search_query = request.args.get('q', '').strip()
    status = request.args.get('status', '').strip().lower()

    categories = get_all_categories()

    current_category = None

    if category_slug:
        current_category = get_category_by_slug(category_slug)
        if not current_category:
            flash('Категория не найдена', 'error')
            return redirect(url_for('admin.admin_products'))
        
    if status and status not in PRODUCT_STATUSES:
        flash('Некорректный статус товара', 'error')
        return redirect(url_for('admin.admin_products'))
        
    products = get_all_products(category_slug=category_slug,
                                sort_by=sort_by,
                                order=order,
                                search_query=search_query,
                                status=status,
                                only_visible=False,
                                is_archived=False)
    
    #materials = products["materials"].split(", ")
    return render_template("admin/products.html",
                           products=products,
                           categories=categories,
                           category_slug=category_slug,
                           current_category=current_category,
                           current_sort=sort_by,
                           current_order=order,
                           current_status=status,
                           search_query=search_query,
                           product_statuses=PRODUCT_STATUSES)


    
@admin_bp.route("/admin/products/archive")
def admin_archived_products():
    products = get_all_products(only_visible=False,is_archived=True)
    
    return render_template("admin/archived_products.html", products=products, product_statuses=PRODUCT_STATUSES)


@admin_bp.route("/admin/products/archive/<product_id>", methods=["POST"])
def archive_product_route(product_id):
    product = get_product_by_id(product_id)

    if not product:
        flash("Работа не найдена", "error")
        return redirect(url_for("admin.admin_products"))

    if product["is_archived"] == 1:
        flash("Работа уже находится в архиве","info")
        return redirect(url_for("admin.admin_archived_products"))

    set_product_archived(product_id, 1)

    flash(f"Работа «{product['name']}» перемещена в архив","success")

    return redirect(url_for("admin.admin_archived_products"))
    
    
@admin_bp.route("/admin/archived_products/restore/<product_id>", methods=["POST"])
def restore_product_route(product_id):
    product = get_product_by_id(product_id)

    if not product:
        flash("Работа не найдена", "error")
        return redirect(url_for("admin.admin_archived_products"))

    if product["is_archived"] != 1:
        flash("Работа не находится в архиве","error")
        return redirect(url_for("admin.admin_products"))

    set_product_archived(product_id, 0)

    flash(f"Работа «{product['name']}» восстановлена","success")

    return redirect(url_for("admin.admin_archived_products"))

    
@admin_bp.route("/admin/products/new", methods=["GET", "POST"])
def new_product():
    """
Обрабатывает создание нового товара в админке.

При GET-запросе показывает пустую форму создания товара со статусом "available"
по умолчанию. При POST-запросе валидирует данные формы, сохраняет изображение,
создаёт новый товар в базе данных и возвращает пользователя к списку товаров.
"""
    if request.method == "POST":
        is_valid, error_message, data = process_product_form(request.form)
        
        if not is_valid:
            flash(error_message, "error")
            return redirect(url_for("admin.new_product"))
            
        is_valid_tags, tag_error_messages, cleaned_tag_ids = process_product_tag_ids(request.form)
        
        if not is_valid_tags:
            flash(tag_error_messages, "error")
            return redirect(url_for("admin.new_product"))
        
        file = request.files.get('img')
        is_created, create_error, product_id = create_product_with_tags(
                    data=data,
                    tag_ids=cleaned_tag_ids,
                    file=file
        )
        
        if not is_created:
            flash(create_error, "error")
            return redirect(url_for("admin.new_product"))
        
        flash("Товар создан", "success")
        return redirect(url_for("admin.admin_products"))
        
    empty_product = {"name": "", 
                     "description": "", 
                     "price": "", 
                     "category_id": None, 
                     "img": "", 
                     "status": "available", 
                     "year": "", 
                     "materials": "Каменная масса", 
                     'is_visible': 1, 
                     'is_for_sale': 1,
                     "is_featured": 0}
                     
    categories = get_all_categories()
    tags = get_all_tags()
    
    return render_template("admin/product_form.html",
                           product=empty_product,
                           categories=categories,
                           tags=tags,
                           selected_tag_ids=[],
                           title="Новый товар",
                           submit_text="Создать",
                           product_statuses=PRODUCT_STATUSES)


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
            
        is_valid_tags, tag_error_messages, cleaned_tag_ids = process_product_tag_ids(request.form)
        
        if not is_valid_tags:
            flash(tag_error_messages, "error")
            return redirect(url_for("admin.edit_product", product_id=product_id))
        
        file = request.files.get('img')
        
        is_updated, update_error = update_product_with_tags(
            product_id=product_id,
            old_image_path=product["img"],
            data=data,
            tag_ids=cleaned_tag_ids,
            file=file
        )
        
        if not is_updated:
            flash(update_error, "error")
            return redirect(url_for("admin.edit_product", product_id=product_id))
        
        flash("Товар обновлён", "success")
        return redirect(url_for("admin.admin_products"))
        
    categories = get_all_categories()
    tags = get_all_tags()
    product_tags = get_tags_for_product(product_id)
    selected_tag_ids = [tag["id"] for tag in product_tags]
    return render_template("admin/product_form.html",
                           product=product,
                           categories=categories,
                           tags=tags,
                           selected_tag_ids=selected_tag_ids,
                           title="Редактирование товара",
                           submit_text="Сохранить",
                           product_statuses=PRODUCT_STATUSES)
                           
                           
@admin_bp.route("/admin/products/state/<product_id>", methods=["POST"])
def update_product_state_route(product_id):
    product = get_product_by_id(product_id)
    
    if not product:
        flash("Работа не найдена", "error")
        return redirect(url_for("admin.admin_products"))
        
    is_valid, message, cleaned_data = process_product_state_form(
        request.form
    )

    if not is_valid:
        flash(message, "error")
        return redirect(url_for("admin.admin_products"))

    is_updated, update_message = update_product_state_with_order_check(
        product_id=product_id,
        data=cleaned_data
    )

    if not is_updated:
        flash(update_message, "error")
        return redirect(url_for("admin.admin_products"))

    flash("Состояние работы обновлено", "success")
    return redirect(url_for("admin.admin_products"))
    
    
@admin_bp.route("/admin/products/delete/<product_id>", methods=["POST"])
def delete_product_route(product_id):
    
    product = get_product_by_id(product_id)

    if not product:
        flash("Работа не найдена", "error")
        return redirect(url_for("admin.admin_archived_products"))

    if product["is_archived"] != 1:
        flash("Перед окончательным удалением переместите работу в архив", "error")
        return redirect(url_for("admin.admin_products"))

    is_deleted, delete_message = delete_product_with_image(
            product_id=product_id,
            image_path=product["img"]
    )
    
    if not is_deleted:
        flash(delete_message, "error")
        return redirect(url_for("admin.admin_archived_products"))
        
    if delete_message:
        flash(delete_message, "info")
    else:
        flash(f"Работа «{product['name']}» удалена навсегда", "info")

    return redirect(url_for("admin.admin_archived_products"))