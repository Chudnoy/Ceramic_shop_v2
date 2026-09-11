from database import projects, works
from database.connection import get_db_connection


def get_public_project_page_data(slug):
    conn = get_db_connection()

    try:
        project = projects.get_published_project_by_slug(conn, slug)

        if project is None:
            return None

        project_id = project["id"]

        project_text = (project["text"] or "").replace("\r\n", "\n")

        project_paragraphs = [
            paragraph.strip()
            for paragraph in project_text.split("\n\n")
            if paragraph.strip()
        ]

        project_images = [
            dict(image) for image in projects.get_project_images(conn, project_id)
        ]

        images_by_position = {image["position"]: image for image in project_images}

        cover_image = images_by_position.get(1)
        premise_image = images_by_position.get(2)
        break_image = images_by_position.get(3)
        process_image = images_by_position.get(4)

        field_images = [image for image in project_images if image["position"] >= 5]

        published_project_works = works.get_published_works_by_project_id(
            conn, project_id
        )

        project_works_data = []

        for project_work in published_project_works:
            project_work_cover = works.get_work_cover_image(conn, project_work["id"])

            project_works_data.append(
                {
                    "id": project_work["id"],
                    "slug": project_work["slug"],
                    "name": project_work["name"],
                    "year": project_work["year"],
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
            "project_paragraphs": project_paragraphs,
            "cover_image": cover_image,
            "premise_image": premise_image,
            "break_image": break_image,
            "process_image": process_image,
            "field_images": field_images,
            "project_works": project_works_data,
        }

    finally:
        conn.close()
