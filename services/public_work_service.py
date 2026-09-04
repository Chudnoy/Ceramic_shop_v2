from database import shop_items, works
from database.connection import get_db_connection


def get_public_work_page_data(slug):
    conn = get_db_connection()

    try:
        work = works.get_published_work_by_slug(conn, slug)

        if work is None:
            return None

        work_id = work["id"]

        images = works.get_work_images(conn, work_id)
        categories = works.get_work_categories(conn, work_id)
        tags = works.get_work_tags(conn, work_id)
        materials = works.get_work_materials(conn, work_id)
        shop_item = shop_items.get_published_shop_item_by_work_id(conn, work_id)

        return {
            "work": dict(work),
            "images": [dict(image) for image in images],
            "categories": [dict(category) for category in categories],
            "tags": [dict(tag) for tag in tags],
            "materials": [dict(material) for material in materials],
            "shop_item": dict(shop_item) if shop_item is not None else None,
        }
    finally:
        conn.close()
