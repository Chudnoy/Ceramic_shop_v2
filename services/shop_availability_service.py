from database import shop_items


def get_shop_item_availability(conn, shop_item):
    reserved_quantity = shop_items.get_reserved_quantity_for_shop_item(
        conn, shop_item["id"]
    )

    available_quantity = shop_item["stock_quantity"] - reserved_quantity

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
    }
