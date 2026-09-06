from database import shop_items, works
from database.connection import get_db_connection
from services.shop_availability_service import get_shop_item_availability


def get_home_page_data():
    conn = get_db_connection()

    try:
        published_works = works.get_published_works(conn, limit=5)
        published_shop_items = shop_items.get_published_shop_items(conn)

        works_data = []

        for work in published_works:
            work_data = dict(work)
            cover_image = works.get_work_cover_image(conn, work["id"])

            work_data["cover_image_path"] = (
                cover_image["image_path"] if cover_image is not None else None
            )

            works_data.append(work_data)

        shop_items_data = []

        for shop_item in published_shop_items:
            availability = get_shop_item_availability(conn, shop_item)

            if not availability["can_order"]:
                continue

            shop_item_data = dict(shop_item)

            cover_image = shop_items.get_shop_item_cover_image(conn, shop_item["id"])

            shop_item_data["cover_image_path"] = (
                cover_image["image_path"] if cover_image is not None else None
            )

            shop_item_data["availability"] = availability

            shop_items_data.append(shop_item_data)

            if len(shop_items_data) == 2:
                break

        return {"works": works_data, "shop_items": shop_items_data}
    finally:
        conn.close()
