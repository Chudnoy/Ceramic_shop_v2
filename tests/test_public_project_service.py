from services.public_project_service import get_public_project_page_data


def create_test_project(
    conn,
    project_id="project-1",
    name="Пористые формы",
    slug="poristye-formy",
    is_published=1,
):
    conn.execute(
        """
        INSERT INTO projects (
            id,
            name,
            slug,
            intro,
            text,
            period,
            is_published
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_id,
            name,
            slug,
            "Исследование пустоты и формы",
            "Большой текст о проекте",
            "2024-2026",
            is_published,
        ),
    )


def create_test_project_image(
    conn,
    project_id="project-1",
    image_path="static/project-cover.jpg",
    position=1,
):
    conn.execute(
        """
        INSERT INTO project_images (
            project_id,
            image_path,
            position
        )
        VALUES (?, ?, ?)
        """,
        (
            project_id,
            image_path,
            position,
        ),
    )


def create_test_work(
    conn,
    work_id,
    slug,
    name,
    year=2025,
    project_id="project-1",
    project_position=None,
    is_published=1,
):
    conn.execute(
        """
        INSERT INTO works (
            id,
            slug,
            name,
            year,
            project_id,
            project_position,
            is_published
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            work_id,
            slug,
            name,
            year,
            project_id,
            project_position,
            is_published,
        ),
    )


def create_test_work_image(
    conn,
    work_id,
    image_path,
    position=1,
):
    conn.execute(
        """
        INSERT INTO work_images (
            work_id,
            image_path,
            position
        )
        VALUES (?, ?, ?)
        """,
        (
            work_id,
            image_path,
            position,
        ),
    )


def test_get_public_project_page_data_returns_project_with_works(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_project(conn)
    create_test_project_image(conn, image_path="static/project-cover.jpg", position=1)
    create_test_project_image(conn, image_path="static/project-detail.jpg", position=2)
    create_test_work(
        conn, work_id="work-1", slug="kaplya", name="Капля", project_position=1
    )
    create_test_work(
        conn, work_id="work-2", slug="kolonna", name="Колонна", project_position=2
    )
    create_test_work(
        conn,
        work_id="work-3",
        slug="belaya-chasha",
        name="Белая чаша",
        project_position=3,
    )
    create_test_work_image(conn, work_id="work-1", image_path="static/kaplya-cover.jpg")
    create_test_work_image(
        conn, work_id="work-2", image_path="static/kolonna-cover.jpg"
    )
    create_test_work_image(conn, work_id="work-3", image_path="static/belaya-cover.jpg")

    conn.commit()
    conn.close()

    page_data = get_public_project_page_data("poristye-formy")

    assert page_data is not None

    assert page_data["project"]["id"] == "project-1"
    assert page_data["project"]["name"] == "Пористые формы"
    assert page_data["project"]["intro"] == "Исследование пустоты и формы"
    assert page_data["project"]["text"] == "Большой текст о проекте"
    assert page_data["project"]["period"] == "2024-2026"

    assert page_data["cover_image"]["image_path"] == "static/project-cover.jpg"
    assert page_data["premise_image"]["image_path"] == "static/project-detail.jpg"
    assert page_data["field_images"] == []

    assert page_data["project_works"] == [
        {
            "id": "work-1",
            "slug": "kaplya",
            "name": "Капля",
            "year": 2025,
            "project_position": 1,
            "cover_image_path": "static/kaplya-cover.jpg",
        },
        {
            "id": "work-2",
            "slug": "kolonna",
            "name": "Колонна",
            "year": 2025,
            "project_position": 2,
            "cover_image_path": "static/kolonna-cover.jpg",
        },
        {
            "id": "work-3",
            "slug": "belaya-chasha",
            "name": "Белая чаша",
            "year": 2025,
            "project_position": 3,
            "cover_image_path": "static/belaya-cover.jpg",
        },
    ]


def test_get_public_project_page_data_returns_none_for_unpublished_project(
    empty_db,
    db_connection,
):
    conn = db_connection()

    create_test_project(
        conn,
        slug="draft",
        is_published=0,
    )

    conn.commit()
    conn.close()

    page_data = get_public_project_page_data("draft")

    assert page_data is None


def test_get_public_project_page_data_excludes_unpublished_works(
    empty_db,
    db_connection,
):
    conn = db_connection()

    create_test_project(conn)

    create_test_work(
        conn,
        work_id="work-1",
        slug="kaplya",
        name="Капля",
        project_position=1,
        is_published=1,
    )

    create_test_work(
        conn,
        work_id="work-2",
        slug="draft-work",
        name="Черновая работа",
        project_position=2,
        is_published=0,
    )

    create_test_work_image(
        conn,
        work_id="work-1",
        image_path="static/kaplya-cover.jpg",
    )

    conn.commit()
    conn.close()

    page_data = get_public_project_page_data("poristye-formy")

    assert page_data is not None

    assert page_data["project_works"] == [
        {
            "id": "work-1",
            "slug": "kaplya",
            "name": "Капля",
            "year": 2025,
            "project_position": 1,
            "cover_image_path": "static/kaplya-cover.jpg",
        }
    ]
