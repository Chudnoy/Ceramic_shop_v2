def get_published_works(conn, limit):
    works = conn.execute(
        """
        SELECT
            id, slug, name, description, year, dimensions, project_id
        FROM works
        WHERE is_published = 1
        ORDER BY name
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    return works


def get_work_images(conn, work_id):
    work_images = conn.execute(
        """
        SELECT id, image_path, position
        FROM work_images
        WHERE work_id = ?
        ORDER BY position
        """,
        (work_id,),
    ).fetchall()

    return work_images


def get_work_cover_image(conn, work_id):
    cover_image = conn.execute(
        """
        SELECT id, image_path, position
        FROM work_images
        WHERE work_id = ?
        AND position = 1
        """,
        (work_id,),
    ).fetchone()

    return cover_image


def get_work_categories(conn, work_id):
    work_categories = conn.execute(
        """
        SELECT c.name, c.slug
        FROM categories AS c
        JOIN work_categories AS wc
            ON c.id = wc.category_id
        WHERE wc.work_id = ?
        ORDER BY c.name
        """,
        (work_id,),
    ).fetchall()

    return work_categories


def get_work_tags(conn, work_id):
    work_tags = conn.execute(
        """
        SELECT t.name, t.slug
        FROM tags AS t
        JOIN work_tags AS wt
            ON t.id = wt.tag_id
        WHERE wt.work_id = ?
        ORDER BY t.name
        """,
        (work_id,),
    ).fetchall()

    return work_tags


def get_work_by_id(conn, work_id):
    return conn.execute("SELECT * FROM works WHERE id = ?", (work_id,)).fetchone()


def get_work_by_slug(conn, slug):
    return conn.execute("SELECT * FROM works WHERE slug = ?", (slug,)).fetchone()


def get_published_work_by_slug(conn, slug):
    return conn.execute(
        "SELECT * FROM works WHERE slug = ? AND is_published = 1", (slug,)
    ).fetchone()


def get_works_by_project_id(conn, project_id):
    works = conn.execute(
        """
        SELECT * FROM works
        WHERE project_id = ?
        ORDER BY
            project_position IS NULL,
            project_position,
            name
        """,
        (project_id,),
    ).fetchall()

    return works


def get_published_works_by_project_id(conn, project_id):
    works = conn.execute(
        """
        SELECT * FROM works
        WHERE project_id = ?
            AND is_published = 1
        ORDER BY
            project_position IS NULL,
            project_position,
            name
        """,
        (project_id,),
    ).fetchall()

    return works
