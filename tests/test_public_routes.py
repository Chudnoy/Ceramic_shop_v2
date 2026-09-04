def test_new_public_home_opens(client, empty_db):
    response = client.get("/v2/")

    assert response.status_code == 200
    assert "Полина Яланская" in response.get_data(as_text=True)


def test_public_work_detail_opens(
    client,
    empty_db,
    db_connection,
):
    conn = db_connection()

    conn.execute(
        """
        INSERT INTO works
            (id, slug, name, is_published)
        VALUES (?, ?, ?, ?)
        """,
        ("work-1", "kaplya", "Капля", 1),
    )

    material_id = conn.execute(
        """
        INSERT INTO materials
            (name, slug)
        VALUES (?, ?)
        """,
        ("Шамот", "chamotte"),
    ).lastrowid

    conn.execute(
        """
        INSERT INTO work_materials
            (work_id, material_id)
        VALUES (?, ?)
        """,
        ("work-1", material_id),
    )

    conn.commit()
    conn.close()

    response = client.get("/v2/works/kaplya")

    assert response.status_code == 200
    assert "Капля" in response.get_data(as_text=True)


def test_public_work_detail_returns_404_for_unknown_slug(client, empty_db):
    response = client.get("/v2/works/not-found")

    assert response.status_code == 404
