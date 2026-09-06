def get_published_project_by_id(conn, project_id):
    return conn.execute(
        """
        SELECT
            id, name, slug, intro, text, period, is_published
        FROM projects
        WHERE id = ?
            AND is_published = 1
        """,
        (project_id,),
    ).fetchone()


def get_project_images(conn, project_id):
    return conn.execute(
        """
        SELECT
            id, image_path, position
        FROM project_images
        WHERE project_id = ?
        ORDER BY position
        """,
        (project_id,),
    ).fetchall()


def get_project_cover_image(conn, project_id):
    return conn.execute(
        """
        SELECT
            id, image_path, position
        FROM project_images
        WHERE project_id = ?
            AND position = 1
        """,
        (project_id,),
    ).fetchone()
