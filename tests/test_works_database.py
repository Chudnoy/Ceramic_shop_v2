from database import works


def create_test_work(conn, work_id="work-1", name="Башня", is_published=1):
    conn.execute(
        """
        INSERT INTO works
            (id, name, is_published)
        VALUES (?, ?, ?)
        """,
        (work_id, name, is_published),
    )


def create_test_work_image(
    conn, work_id="work-1", image_path="img/tower.jpg", position=1
):
    cursor = conn.execute(
        "INSERT INTO work_images (work_id, image_path, position) VALUES (?, ?, ?)",
        (work_id, image_path, position),
    )

    return cursor.lastrowid


def test_get_published_works_filters_orders_and_limits(empty_db, db_connection):
    conn = db_connection()

    create_test_work(conn)
    create_test_work(conn, work_id="work-2", name="Глина", is_published=0)
    create_test_work(conn, work_id="work-5", name="Магнит")
    create_test_work(conn, work_id="work-4", name="Тарелка")
    create_test_work(conn, work_id="work-3", name="Аквариум")

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
