from database import projects


def create_test_project(
    conn,
    project_id="project-1",
    name="Пористые формы",
    slug="poristye-formy",
    is_published=1,
):
    conn.execute(
        """
        INSERT INTO projects
            (id, name, slug, is_published)
        VALUES (?, ?, ?, ?)
        """,
        (project_id, name, slug, is_published),
    )


def create_test_project_image(
    conn, project_id="project-1", image_path="img/project.jpg", position=1
):
    return conn.execute(
        """
        INSERT INTO project_images
            (project_id, image_path, position)
        VALUES (?, ?, ?)
        """,
        (project_id, image_path, position),
    ).lastrowid


def test_get_published_project_by_id_filters_unpublished_projects(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_project(conn)
    create_test_project(
        conn, project_id="project-2", name="Черновик", slug="draft", is_published=0
    )

    published_project = projects.get_published_project_by_id(conn, "project-1")
    unpublished_project = projects.get_published_project_by_id(conn, "project-2")

    conn.close()

    assert published_project is not None
    assert published_project["id"] == "project-1"
    assert published_project["name"] == "Пористые формы"
    assert published_project["slug"] == "poristye-formy"

    assert unpublished_project is None


def test_get_project_images_returns_images_ordered_by_position(empty_db, db_connection):
    conn = db_connection()

    create_test_project(conn)

    second_image_id = create_test_project_image(
        conn, image_path="img/detail.jpg", position=2
    )
    first_image_id = create_test_project_image(
        conn, image_path="img/cover.jpg", position=1
    )

    images = projects.get_project_images(conn, "project-1")

    conn.close()

    assert [
        (image["id"], image["image_path"], image["position"]) for image in images
    ] == [(first_image_id, "img/cover.jpg", 1), (second_image_id, "img/detail.jpg", 2)]


def test_get_project_cover_image_returns_position_one(empty_db, db_connection):
    conn = db_connection()

    create_test_project(conn)

    create_test_project_image(conn, image_path="img/detail.jpg", position=2)
    cover_id = create_test_project_image(conn, image_path="img/cover.jpg", position=1)

    cover_image = projects.get_project_cover_image(conn, "project-1")

    conn.close()

    assert cover_image is not None
    assert cover_image["id"] == cover_id
    assert cover_image["image_path"] == "img/cover.jpg"
    assert cover_image["position"] == 1


def test_get_published_project_by_slug_filters_unpublished_project(
    empty_db,
    db_connection,
):
    conn = db_connection()

    create_test_project(conn)

    create_test_project(
        conn,
        project_id="project-2",
        name="Черновик",
        slug="draft",
        is_published=0,
    )

    published_project = projects.get_published_project_by_slug(conn, "poristye-formy",)

    unpublished_project = projects.get_published_project_by_slug(conn, "draft",)

    conn.close()

    assert published_project is not None
    assert published_project["id"] == "project-1"
    assert published_project["name"] == "Пористые формы"

    assert unpublished_project is None