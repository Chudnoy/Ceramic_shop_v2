from database import shop_items, works
from database.connection import get_db_connection
from services.shop_availability_service import get_shop_item_availability


def get_public_shop_page_data():
    conn = get_db_connection()

    try:
        published_shop_items = shop_items.get_published_shop_items(conn)

        shop_items_data = []

        for shop_item in published_shop_items:
            if shop_item["is_orderable"] != 1:
                continue
            if shop_item["is_retired"] == 1:
                continue

            if shop_item["work_id"] is not None:
                work = works.get_work_by_id(conn, shop_item["work_id"])

                if work is None or work["is_published"] != 1:
                    continue

            availability = get_shop_item_availability(conn, shop_item)

            if (
                shop_item["inventory_type"] == "unique"
                and availability["stock_state"] == "out_of_stock"
            ):
                continue

            shop_item_data = dict(shop_item)

            cover_image = shop_items.get_shop_item_cover_image(conn, shop_item["id"])

            shop_item_data["cover_image_path"] = (
                cover_image["image_path"] if cover_image is not None else None
            )

            shop_item_data["availability"] = availability

            shop_items_data.append(shop_item_data)

        return {"shop_items": shop_items_data}
    finally:
        conn.close()
