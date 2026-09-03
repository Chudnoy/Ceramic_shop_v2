from database import works


def create_test_work(
    conn,
    work_id="work-1",
    name="Башня",
    slug="bashnya",
    is_published=1,
    project_id=None,
    project_position=None,
):
    conn.execute(
        """
        INSERT INTO works
            (
                id,
                slug,
                name,
                is_published,
                project_id,
                project_position
            )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            work_id,
            slug,
            name,
            is_published,
            project_id,
            project_position,
        ),
    )


def create_test_work_image(
    conn, work_id="work-1", image_path="img/tower.jpg", position=1
):
    cursor = conn.execute(
        "INSERT INTO work_images (work_id, image_path, position) VALUES (?, ?, ?)",
        (work_id, image_path, position),
    )

    return cursor.lastrowid


def create_test_category(conn, name="Вазы", slug="vases"):
    cursor = conn.execute(
        "INSERT INTO categories (name, slug) VALUES (?, ?)", (name, slug)
    )

    return cursor.lastrowid


def create_test_tag(conn, name="Дом", slug="home"):
    cursor = conn.execute("INSERT INTO tags (name, slug) VALUES (?, ?)", (name, slug))

    return cursor.lastrowid


def create_test_project(
    conn,
    project_id="project-1",
    name="Дом",
    slug="home",
):
    conn.execute(
        """
        INSERT INTO projects
            (id, name, slug)
        VALUES (?, ?, ?)
        """,
        (project_id, name, slug),
    )


def test_get_published_works_filters_orders_and_limits(empty_db, db_connection):
    conn = db_connection()

    create_test_work(conn)
    create_test_work(conn, work_id="work-2", name="Глина", slug="clay", is_published=0)
    create_test_work(conn, work_id="work-5", name="Магнит", slug="magnet")
    create_test_work(conn, work_id="work-4", name="Тарелка", slug="plate")
    create_test_work(conn, work_id="work-3", name="Аквариум", slug="aquarium")

    conn.commit()

    published_works = works.get_published_works(conn, 3)

    conn.close()

    assert len(published_works) == 3
    assert [work["name"] for work in published_works] == ["Аквариум", "Башня", "Магнит"]
    assert published_works[0]["id"] == "work-3"
    assert published_works[1]["id"] == "work-1"
    assert published_works[2]["id"] == "work-5"


def test_get_work_images_returns_images_ordered_by_position(empty_db, db_connection):
    conn = db_connection()

    create_test_work(conn)
    first_image_id = create_test_work_image(conn, position=2)
    second_image_id = create_test_work_image(conn, image_path="img/mug.jpg", position=1)

    conn.commit()

    work_images = works.get_work_images(conn, "work-1")

    conn.close()

    assert len(work_images) == 2
    assert work_images[0]["id"] == second_image_id
    assert work_images[1]["id"] == first_image_id
    assert [work_image["position"] for work_image in work_images] == [1, 2]
    assert work_images[0]["image_path"] == "img/mug.jpg"
    assert work_images[1]["image_path"] == "img/tower.jpg"


def test_get_work_cover_image_returns_only_cover_image(empty_db, db_connection):
    conn = db_connection()

    create_test_work(conn)
    create_test_work_image(conn, position=2)
    second_image_id = create_test_work_image(conn, image_path="img/mug.jpg", position=1)

    conn.commit()

    cover_image = works.get_work_cover_image(conn, "work-1")

    conn.close()

    assert cover_image is not None
    assert cover_image["id"] == second_image_id
    assert cover_image["image_path"] == "img/mug.jpg"
    assert cover_image["position"] == 1


def test_get_work_cover_image_returns_none_when_cover_does_not_exist(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_work(conn)
    create_test_work_image(conn, position=2)

    cover_image = works.get_work_cover_image(conn, "work-1")

    conn.close()

    assert cover_image is None


def test_get_work_categories_returns_correct_and_ordered_categories(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_work(conn)
    create_test_work(conn, work_id="work-2", name="Тарелка", slug="plate")
    first_category_id = create_test_category(conn, name="Чашки", slug="mugs")
    second_category_id = create_test_category(conn)
    third_category_id = create_test_category(conn, name="Тарелки", slug="plates")

    conn.execute(
        "INSERT INTO work_categories (work_id, category_id) VALUES (?, ?)",
        ("work-1", first_category_id),
    )
    conn.execute(
        "INSERT INTO work_categories (work_id, category_id) VALUES (?, ?)",
        ("work-1", second_category_id),
    )
    conn.execute(
        "INSERT INTO work_categories (work_id, category_id) VALUES (?, ?)",
        ("work-2", third_category_id),
    )

    conn.commit()

    work_categories = works.get_work_categories(conn, "work-1")

    conn.close()

    assert [
        (work_category["name"], work_category["slug"])
        for work_category in work_categories
    ] == [("Вазы", "vases"), ("Чашки", "mugs")]


def test_get_work_tags_returns_correct_and_ordered_tags(empty_db, db_connection):
    conn = db_connection()

    create_test_work(conn)
    create_test_work(conn, work_id="work-2", name="Тарелка", slug="plate")
    first_tag_id = create_test_tag(conn, name="Память", slug="memory")
    second_tag_id = create_test_tag(conn)
    third_tag_id = create_test_tag(conn, name="Природа", slug="nature")

    conn.execute(
        "INSERT INTO work_tags (work_id, tag_id) VALUES (?, ?)",
        ("work-1", first_tag_id),
    )
    conn.execute(
        "INSERT INTO work_tags (work_id, tag_id) VALUES (?, ?)",
        ("work-1", second_tag_id),
    )
    conn.execute(
        "INSERT INTO work_tags (work_id, tag_id) VALUES (?, ?)",
        ("work-2", third_tag_id),
    )

    conn.commit()

    work_tags = works.get_work_tags(conn, "work-1")

    conn.close()

    assert [(work_tag["name"], work_tag["slug"]) for work_tag in work_tags] == [
        ("Дом", "home"),
        ("Память", "memory"),
    ]


def test_get_work_by_id_returns_correct_work(empty_db, db_connection):
    conn = db_connection()

    create_test_work(conn)
    create_test_work(
        conn,
        work_id="work-2",
        name="Тарелка",
        slug="plate",
    )

    work = works.get_work_by_id(conn, "work-2")

    conn.close()

    assert work is not None
    assert work["id"] == "work-2"
    assert work["name"] == "Тарелка"
    assert work["slug"] == "plate"


def test_get_work_by_slug_returns_correct_work(empty_db, db_connection):
    conn = db_connection()

    create_test_work(conn)
    create_test_work(
        conn,
        work_id="work-2",
        name="Тарелка",
        slug="plate",
    )

    work = works.get_work_by_slug(conn, "plate")

    conn.close()

    assert work is not None
    assert work["id"] == "work-2"
    assert work["name"] == "Тарелка"
    assert work["slug"] == "plate"


def test_get_published_work_by_slug_filters_unpublished_work(empty_db, db_connection):
    conn = db_connection()

    create_test_work(conn)
    create_test_work(
        conn, work_id="work-2", name="Тарелка", slug="plate", is_published=0
    )

    first_work = works.get_published_work_by_slug(conn, "plate")
    second_work = works.get_published_work_by_slug(conn, "bashnya")

    conn.close()

    assert first_work is None
    assert second_work is not None
    assert second_work["name"] == "Башня"
    assert second_work["id"] == "work-1"
    assert second_work["slug"] == "bashnya"


def test_get_works_by_project_id_returns_correct_and_ordered_works(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_project(conn)
    create_test_project(
        conn,
        project_id="project-2",
        name="Другой проект",
        slug="other-project",
    )

    create_test_work(
        conn,
        work_id="work-1",
        name="Яблоко",
        slug="apple",
        project_id="project-1",
    )
    create_test_work(
        conn,
        work_id="work-2",
        name="Вторая",
        slug="second",
        project_id="project-1",
        project_position=2,
    )
    create_test_work(
        conn,
        work_id="work-3",
        name="Первая",
        slug="first",
        project_id="project-1",
        project_position=1,
    )
    create_test_work(
        conn,
        work_id="work-4",
        name="Чужая",
        slug="foreign",
        project_id="project-2",
        project_position=1,
    )
    create_test_work(
        conn,
        work_id="work-5",
        name="Арка",
        slug="arch",
        project_id="project-1",
    )

    project_works = works.get_works_by_project_id(conn, "project-1")

    conn.close()

    assert [(work["id"], work["project_position"]) for work in project_works] == [
        ("work-3", 1),
        ("work-2", 2),
        ("work-5", None),
        ("work-1", None),
    ]


def test_get_published_works_by_project_id_filters_unpublished_works(
    empty_db, db_connection
):
    conn = db_connection()

    create_test_project(conn)

    create_test_work(
        conn,
        work_id="work-1",
        project_id="project-1",
        project_position=1,
    )
    create_test_work(
        conn,
        work_id="work-2",
        name="Скрытая",
        slug="hidden",
        is_published=0,
        project_id="project-1",
        project_position=2,
    )

    project_works = works.get_published_works_by_project_id(
        conn,
        "project-1",
    )

    conn.close()

    assert [work["id"] for work in project_works] == ["work-1"]
