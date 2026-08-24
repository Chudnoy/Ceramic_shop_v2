import uuid


def backfill_unique_shop_items(conn):
    products = conn.execute(
        """
        SELECT
            products.id,
            products.price,
            products.is_visible,
            products.is_for_sale
        FROM products
        WHERE 
            (
                products.status = 'available'
                AND products.is_for_sale = 1
                AND products.is_archived = 0
            )
            OR
            (
                products.status = 'reserved'
                AND products.is_archived = 0
                AND EXISTS (
                    SELECT 1
                    FROM order_items
                    JOIN orders
                        ON orders.id = order_items.order_id
                    WHERE order_items.product_id = products.id
                        AND orders.status IN ('new', 'confirmed')
                )
            )
        ORDER BY products.id
        """
    ).fetchall()

    for product in products:
        conn.execute(
            """
            INSERT INTO shop_items
                (id, work_id, price, inventory_type, stock_quantity, is_published, is_orderable, is_retired)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                product["id"],
                product["price"],
                "unique",
                1,
                product["is_visible"] * product["is_for_sale"],
                product["is_for_sale"],
                0,
            ),
        )


BACKFILL_TARGET_TABLES = {
    "shop_items",
    "shop_item_images",
    "shop_item_categories",
    "shop_item_tags",
    "shop_item_materials",
}


def preflight_backfill_targets_are_empty(conn):
    nonempty_tables = {}

    for table_name in BACKFILL_TARGET_TABLES:
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

        if row_count > 0:
            nonempty_tables[table_name] = row_count

    if nonempty_tables:
        raise ValueError(
            "Preflight failed: целевые таблицы Shop backfill уже содержат данные"
        )


def preflight_shop_products_have_matching_works(conn):
    invalid_products = conn.execute(
        """
        SELECT
            products.id,
            products.name
        FROM products
        LEFT JOIN works
            ON works.id = products.id
        WHERE works.id IS NULL
        AND (
            (
            products.status = 'available'
            AND products.is_for_sale = 1
            AND products.is_archived = 0
            )
            OR (
                products.status = 'reserved'
                AND products.is_archived = 0
                AND EXISTS (
                    SELECT 1
                    FROM order_items
                    JOIN orders
                        ON orders.id = order_items.order_id
                    WHERE order_items.product_id = products.id
                        AND orders.status IN ('new', 'confirmed')
                    )
                )
            )
        ORDER BY products.id
        """
    ).fetchall()

    if invalid_products:
        raise ValueError(
            "Preflight failed: найдены Shop products без соответствующей work"
        )


def preflight(conn):
    preflight_backfill_targets_are_empty(conn)
    preflight_shop_products_have_matching_works(conn)


def apply(conn):
    preflight(conn)

    backfill_unique_shop_items(conn)
