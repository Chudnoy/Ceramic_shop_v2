from flask import flash, redirect, render_template, request, session, url_for

from database.orders import get_order_by_id
from services.cart_service import build_cart_summary, remove_ordered_items_from_cart
from services.order_service import (
    build_order_item_list,
    create_order_with_items,
    process_checkout_form,
)

from . import main_bp


@main_bp.route("/checkout")
def checkout_form():
    cart_summary = build_cart_summary(session)
    available_products = cart_summary["available_products"]

    if not cart_summary["cart"]:
        flash("Корзина пуста", "error")
        return redirect(url_for("main.catalog"))

    if not available_products:
        flash("В корзине нет работ, доступных для оформления", "error")
        return redirect(url_for("main.show_cart"))

    if cart_summary["has_unavailable_items"]:
        flash("Некоторые работы больше недоступны и не будут включены в заказ", "info")

    return render_template(
        "checkout.html",
        products=available_products,
        total=cart_summary["total"],
        cart=cart_summary["cart"],
        has_unavailable_items=cart_summary["has_unavailable_items"],
    )


@main_bp.route("/checkout", methods=["POST"])
def checkout_process():

    cart_summary = build_cart_summary(session)
    cart = cart_summary["cart"]
    available_products = cart_summary["available_products"]

    if not cart:
        flash("Корзина пуста", "error")
        return redirect(url_for("main.catalog"))

    if not available_products:
        flash("В корзине нет работ, доступных для оформления", "error")
        return redirect(url_for("main.show_cart"))

    is_valid, error_message, data = process_checkout_form(request.form)

    if not is_valid:
        flash(error_message, "error")
        return redirect(url_for("main.checkout_form"))

    if (
        cart_summary["has_unavailable_items"]
        and request.form.get("confirm_partial_order") != "1"
    ):
        flash("Подтвердите оформление заказа только из доступных работ", "info")
        return redirect(url_for("main.checkout_form"))

    items = build_order_item_list(cart, available_products)

    is_created, create_error, order_id = create_order_with_items(data=data, items=items)

    if not is_created:
        flash(create_error, "error")
        return redirect(url_for("main.show_cart"))

    ordered_product_ids = [item["product_id"] for item in items]
    remove_ordered_items_from_cart(session=session, product_ids=ordered_product_ids)

    flash(f"Заказ {order_id[:8]} оформлен!", "success")

    return redirect(url_for("main.order_success", order_id=order_id))


@main_bp.route("/order_success/<order_id>")
def order_success(order_id):
    order = get_order_by_id(order_id)

    if not order:
        flash("Заказ не найден", "error")
        return redirect(url_for("main.catalog"))

    order_items = order.get("items", [])

    return render_template(
        "order_success.html", order=order, order_id=order_id, order_items=order_items
    )
