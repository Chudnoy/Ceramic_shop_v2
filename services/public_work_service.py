from database import projects, shop_items, works
from database.connection import get_db_connection
from services.shop_availability_service import get_shop_item_availability


def get_public_works_page_data(sort="name_asc"):
    conn = get_db_connection()

    try:
        published_works = works.get_published_works(conn, sort=sort)

        works_data = []

        for work in published_works:
            cover_image = works.get_work_cover_image(conn, work["id"])

            work_data = dict(work)
            work_data["cover_image_path"] = (
                cover_image["image_path"] if cover_image is not None else None
            )

            works_data.append(work_data)

        return {"works": works_data}
    finally:
        conn.close()


def get_public_work_page_data(slug):
    conn = get_db_connection()

    try:
        work = works.get_published_work_by_slug(conn, slug)

        if work is None:
            return None

        work_id = work["id"]

        images = works.get_work_images(conn, work_id)
        cover_image = works.get_work_cover_image(conn, work_id)
        categories = works.get_work_categories(conn, work_id)
        tags = works.get_work_tags(conn, work_id)
        materials = works.get_work_materials(conn, work_id)
        shop_item = shop_items.get_published_shop_item_by_work_id(conn, work_id)
        shop_item_data = dict(shop_item) if shop_item is not None else None
        availability = (
            get_shop_item_availability(conn, shop_item)
            if shop_item is not None
            else None
        )

        project_preview = None

        project_id = work["project_id"]

        if project_id is not None:
            project = projects.get_published_project_by_id(conn, project_id)

            if project is not None:
                project_cover_image = projects.get_project_cover_image(conn, project_id)

                project_preview = {
                    "id": project["id"],
                    "name": project["name"],
                    "slug": project["slug"],
                    "intro": project["intro"],
                    "period": project["period"],
                    "cover_image_path": (
                        project_cover_image["image_path"]
                        if project_cover_image is not None
                        else None
                    ),
                }

        other_published_works = works.get_other_published_works(conn, work_id)

        other_works = []

        for other_work in other_published_works:
            other_work_cover = works.get_work_cover_image(conn, other_work["id"])

            other_works.append(
                {
                    "id": other_work["id"],
                    "slug": other_work["slug"],
                    "name": other_work["name"],
                    "year": other_work["year"],
                    "dimensions": other_work["dimensions"],
                    "cover_image_path": other_work_cover["image_path"]
                    if other_work_cover is not None
                    else None,
                }
            )

        return {
            "work": dict(work),
            "images": [dict(image) for image in images],
            "cover_image": dict(cover_image) if cover_image is not None else None,
            "detail_images": [
                dict(image) for image in images if image["position"] != 1
            ],
            "categories": [dict(category) for category in categories],
            "tags": [dict(tag) for tag in tags],
            "materials": [dict(material) for material in materials],
            "shop_item": shop_item_data,
            "availability": availability,
            "project_preview": project_preview,
            "other_works": other_works,
        }
    finally:
        conn.close()
