from flask import flash, redirect, render_template, request, session, url_for

from database.products import get_product_by_id
from services.cart_service import (
    add_to_cart_serv,
    build_cart_summary,
    clear_cart,
    get_cart_count,
    remove_from_cart_serv,
    remove_unavailable_items,
)
from services.product_service import (
    PRODUCT_STATUSES,
    get_product_cart_unavailable_reason,
)

from . import main_bp


@main_bp.route("/cart")
def show_cart():
    cart_summary = build_cart_summary(session)

    return render_template(
        "cart.html",
        products=cart_summary["products"],
        total=cart_summary["total"],
        cart=cart_summary["cart"],
        has_unavailable_items=cart_summary["has_unavailable_items"],
        product_statuses=PRODUCT_STATUSES,
    )


@main_bp.route("/cart/remove_unavailable", methods=["POST"])
def remove_unavailable_route():
    removed = remove_unavailable_items(session)

    if removed:
        flash("Недоступные работы удалены", "success")
    else:
        flash("Нет недоступных работ", "error")

    return redirect(url_for("main.show_cart"))


@main_bp.route("/cart/clear_cart", methods=["POST"])
def clear_cart_route():

    if get_cart_count(session) > 0:
        clear_cart(session)
        flash("Корзина очищена", "success")
    else:
        flash("В корзине нет работ", "error")

    return redirect(url_for("main.show_cart"))


@main_bp.route("/add_to_cart/<product_id>", methods=["POST"])
def add_to_cart_route(product_id):
    quantity_str = request.form.get("quantity", "1")

    try:
        quantity = int(quantity_str)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        flash("Количество должно быть положительным числом", "error")
        return redirect(url_for("main.product_page", product_id=product_id))

    product = get_product_by_id(product_id)

    unavailable_reason = get_product_cart_unavailable_reason(product)

    if unavailable_reason:
        flash(unavailable_reason, "error")

        if not product:
            return redirect(url_for("main.catalog"))

        return redirect(url_for("main.product_page", product_id=product_id))

    new_qty = add_to_cart_serv(session, product_id, quantity)

    flash(
        f"Работа «{product['name']}» добавлена в корзину (количество: {new_qty})",
        "success",
    )
    return redirect(url_for("main.product_page", product_id=product_id))


@main_bp.route("/remove_from_cart/<product_id>", methods=["POST"])
def remove_from_cart_route(product_id):
    removed = remove_from_cart_serv(session, product_id)

    if removed:
        flash("Работа удалена из корзины", "info")
    else:
        flash("Работа не найдена в корзине", "error")
    return redirect(url_for("main.show_cart"))
