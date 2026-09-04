def get_published_shop_items(conn, limit):
    return conn.execute(
        """
        SELECT
            si.id,
            si.work_id,
            CASE
                WHEN si.work_id IS NOT NULL
                THEN w.name
                ELSE si.name
            END AS name,
            CASE
                WHEN si.work_id IS NOT NULL
                THEN w.description
                ELSE si.description
            END AS description,
            CASE
                WHEN si.work_id IS NOT NULL
                THEN w.dimensions
                ELSE si.dimensions
            END AS dimensions,
            w.year AS year,
            si.sales_note,
            si.price,
            si.inventory_type,
            si.stock_quantity,
            si.is_published,
            si.is_orderable,
            si.is_retired
        FROM shop_items AS si
        LEFT JOIN works AS w
            ON w.id = si.work_id
        WHERE si.is_published = 1
        ORDER BY name
        LIMIT ?
        """,
        (limit,),
    ).fetchall()


def get_shop_item_by_id(conn, shop_item_id):
    return conn.execute(
        """
        SELECT
            si.id,
            si.work_id,
            CASE
                WHEN si.work_id IS NOT NULL
                THEN w.name
                ELSE si.name
            END AS name,
            CASE
                WHEN si.work_id IS NOT NULL
                THEN w.description
                ELSE si.description
            END AS description,
            CASE
                WHEN si.work_id IS NOT NULL
                THEN w.dimensions
                ELSE si.dimensions
            END AS dimensions,
            w.year AS year,
            si.sales_note,
            si.price,
            si.inventory_type,
            si.stock_quantity,
            si.is_published,
            si.is_orderable,
            si.is_retired
        FROM shop_items AS si
        LEFT JOIN works AS w
            ON w.id = si.work_id
        WHERE si.id = ?
        """,
        (shop_item_id,),
    ).fetchone()


def get_published_shop_item_by_id(conn, shop_item_id):
    return conn.execute(
        """
        SELECT
            si.id,
            si.work_id,
            CASE
                WHEN si.work_id IS NOT NULL
                THEN w.name
                ELSE si.name
            END AS name,
            CASE
                WHEN si.work_id IS NOT NULL
                THEN w.description
                ELSE si.description
            END AS description,
            CASE
                WHEN si.work_id IS NOT NULL
                THEN w.dimensions
                ELSE si.dimensions
            END AS dimensions,
            w.year AS year,
            si.sales_note,
            si.price,
            si.inventory_type,
            si.stock_quantity,
            si.is_published,
            si.is_orderable,
            si.is_retired
        FROM shop_items AS si
        LEFT JOIN works AS w
            ON w.id = si.work_id
        WHERE si.id = ?
            AND si.is_published = 1
        """,
        (shop_item_id,),
    ).fetchone()


def get_shop_item_images(conn, shop_item_id):
    return conn.execute(
        """
        SELECT
        wi.id, wi.image_path, wi.position
        FROM shop_items AS si
        JOIN work_images AS wi
            ON wi.work_id = si.work_id
        WHERE si.id = ?
            AND si.work_id IS NOT NULL

        UNION ALL

        SELECT
        sii.id, sii.image_path, sii.position
        FROM shop_items AS si
        JOIN shop_item_images AS sii
            ON sii.shop_item_id = si.id
        WHERE si.id = ?
            AND si.work_id IS NULL

        ORDER BY position
        """,
        (shop_item_id, shop_item_id),
    ).fetchall()


def get_shop_item_cover_image(conn, shop_item_id):
    return conn.execute(
        """
        SELECT
        wi.id, wi.image_path, wi.position
        FROM shop_items AS si
        JOIN work_images AS wi
            ON wi.work_id = si.work_id
        WHERE si.id = ?
            AND si.work_id IS NOT NULL
            AND wi.position = 1

        UNION ALL

        SELECT
        sii.id, sii.image_path, sii.position
        FROM shop_items AS si
        JOIN shop_item_images AS sii
            ON sii.shop_item_id = si.id
        WHERE si.id = ?
            AND si.work_id IS NULL
            AND sii.position = 1
        """,
        (shop_item_id, shop_item_id),
    ).fetchone()


def get_shop_item_categories(conn, shop_item_id):
    return conn.execute(
        """
        SELECT
            c.name,
            c.slug
        FROM shop_items AS si
        JOIN work_categories AS wc
            ON wc.work_id = si.work_id
        JOIN categories AS c
            ON c.id = wc.category_id
        WHERE si.id = ?
            AND si.work_id IS NOT NULL

        UNION ALL

        SELECT
            c.name,
            c.slug
        FROM shop_items AS si
        JOIN shop_item_categories AS sic
            ON sic.shop_item_id = si.id
        JOIN categories AS c
            ON c.id = sic.category_id
        WHERE si.id = ?
            AND si.work_id IS NULL

        ORDER BY 1
        """,
        (shop_item_id, shop_item_id),
    ).fetchall()


def get_shop_item_tags(conn, shop_item_id):
    return conn.execute(
        """
        SELECT
            t.name,
            t.slug
        FROM shop_items AS si
        JOIN work_tags AS wt
            ON wt.work_id = si.work_id
        JOIN tags AS t
            ON t.id = wt.tag_id
        WHERE si.id = ?
            AND si.work_id IS NOT NULL

        UNION ALL

        SELECT
            t.name,
            t.slug
        FROM shop_items AS si
        JOIN shop_item_tags AS sit
            ON sit.shop_item_id = si.id
        JOIN tags AS t
            ON t.id = sit.tag_id
        WHERE si.id = ?
            AND si.work_id IS NULL

        ORDER BY 1
        """,
        (shop_item_id, shop_item_id),
    ).fetchall()


def get_shop_item_materials(conn, shop_item_id):
    return conn.execute(
        """
        SELECT
            m.name,
            m.slug
        FROM shop_items AS si
        JOIN work_materials AS wm
            ON wm.work_id = si.work_id
        JOIN materials AS m
            ON m.id = wm.material_id
        WHERE si.id = ?
            AND si.work_id IS NOT NULL

        UNION ALL

        SELECT
            m.name,
            m.slug
        FROM shop_items AS si
        JOIN shop_item_materials AS sim
            ON sim.shop_item_id = si.id
        JOIN materials AS m
            ON m.id = sim.material_id
        WHERE si.id = ?
            AND si.work_id IS NULL

        ORDER BY 1
        """,
        (shop_item_id, shop_item_id),
    ).fetchall()
