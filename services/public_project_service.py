from database import projects, works
from database.connection import get_db_connection


def get_public_project_page_data(slug):
    conn = get_db_connection()

    try:
        project = projects.get_published_project_by_slug(
            conn,
            slug,
        )

        if project is None:
            return None

        project_id = project["id"]

        images = projects.get_project_images(
            conn,
            project_id,
        )

        cover_image = projects.get_project_cover_image(
            conn,
            project_id,
        )

        published_project_works = works.get_published_works_by_project_id(
            conn,
            project_id,
        )

        project_works_data = []

        for project_work in published_project_works:
            project_work_cover = works.get_work_cover_image(
                conn,
                project_work["id"],
            )

            project_works_data.append(
                {
                    "id": project_work["id"],
                    "slug": project_work["slug"],
                    "name": project_work["name"],
                    "project_position": project_work["project_position"],
                    "cover_image_path": (
                        project_work_cover["image_path"]
                        if project_work_cover is not None
                        else None
                    ),
                }
            )

        return {
            "project": dict(project),
            "images": [dict(image) for image in images],
            "cover_image": (dict(cover_image) if cover_image is not None else None),
            "project_works": project_works_data,
        }

    finally:
        conn.close()
