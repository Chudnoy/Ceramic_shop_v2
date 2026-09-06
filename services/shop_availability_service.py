from database import shop_items


def get_shop_item_availability(conn, shop_item):
    reserved_quantity = shop_items.get_reserved_quantity_for_shop_item(
        conn, shop_item["id"]
    )

    available_quantity = shop_item["stock_quantity"] - reserved_quantity

    if available_quantity < 0:
        raise ValueError("reserved_quantity cannot exceed stock_quantity")

    if available_quantity > 0:
        stock_state = "available"
    elif reserved_quantity > 0:
        stock_state = "fully_reserved"
    else:
        stock_state = "out_of_stock"

    can_order = (
        shop_item["is_published"] == 1
        and shop_item["is_orderable"] == 1
        and shop_item["is_retired"] == 0
        and available_quantity > 0
    )

    return {
        "reserved_quantity": reserved_quantity,
        "available_quantity": available_quantity,
        "can_order": can_order,
        "stock_state": stock_state,
    }
