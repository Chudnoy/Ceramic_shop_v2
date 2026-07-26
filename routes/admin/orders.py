from flask import request, render_template, flash, redirect, url_for
from database.orders import get_all_orders, get_order_by_id
from services.order_service import ORDER_STATUSES, process_order_form, update_order_with_items, cancel_order, delete_canceled_order

from . import admin_bp

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
        
        is_updated, update_error = update_order_with_items(order_id, data)

        if not is_updated:
            flash(update_error, 'error')
            return redirect(url_for('admin.edit_order', order_id=order_id))
        
        flash('Заказ обновлён', 'success')
        return redirect(url_for('admin.admin_orders'))
    
    return render_template("admin/order_form.html", order=order)
    
    
@admin_bp.route("/admin/orders/<order_id>/cancel", methods=["POST"])
def cancel_order_route(order_id):
    is_canceled, error_message = cancel_order(order_id)

    if not is_canceled:
        flash(error_message, "error")
        return redirect(url_for("admin.admin_orders"))

    flash("Заказ отменён, резерв товаров снят", "success")
    return redirect(url_for("admin.admin_orders"))
    
    
@admin_bp.route("/admin/orders/delete/<order_id>", methods=["POST"])
def delete_order_route(order_id):
    is_deleted, error_message = delete_canceled_order(order_id)

    if not is_deleted:
        flash(error_message, 'error')
        return redirect(url_for('admin.admin_orders'))
    flash("Отменённый заказ удалён", "info")
    return redirect(url_for("admin.admin_orders"))