def preflight_products_have_materials(conn):
    invalid_products = conn.execute(
        "SELECT id, name, materials FROM products WHERE TRIM(materials) = '' ORDER BY id"
    ).fetchall()

    if invalid_products:
        raise ValueError("Preflight failed: найдены продукты без материалов")


def preflight_active_order_items_have_products(conn):
    invalid_items = conn.execute(
        """
        SELECT
            orders.id AS order_id,
            orders.status,
            order_items.id AS order_item_id,
            order_items.product_name
        FROM order_items
        JOIN orders
            ON orders.id = order_items.order_id
        WHERE orders.status IN ('new', 'confirmed')
            AND order_items.product_id IS NULL
        ORDER BY orders.id, order_items.id
        """
    ).fetchall()

    if invalid_items:
        raise ValueError(
            "Preflight failed: найдены активные позиции заказа без Product"
        )


def preflight_product_status_matches_active_orders(conn):
    invalid_products = conn.execute(
        """
        WITH active AS (
            SELECT
                order_items.product_id,
                SUM(order_items.quantity) AS active_quantity
            FROM order_items
            JOIN orders
                ON orders.id = order_items.order_id
            WHERE
                orders.status IN ('new', 'confirmed')
                AND order_items.product_id IS NOT NULL
            GROUP BY order_items.product_id
        ),
        products_with_active_quantity AS (
            SELECT
                products.id,
                products.name,
                products.status,
                COALESCE(active.active_quantity, 0) AS active_quantity
            FROM products
            LEFT JOIN active
                ON active.product_id = products.id
        )
        SELECT
            id,
            name,
            status,
            active_quantity
        FROM products_with_active_quantity
        WHERE
            (
                status = 'available'
                AND active_quantity != 0
            )
            OR
            (
                status = 'reserved'
                AND active_quantity != 1
            )
            OR
            (
                status = 'sold'
                AND active_quantity != 0
            )
        ORDER BY id
        """
    ).fetchall()

    if invalid_products:
        raise ValueError(
            "Preflight failed: статусы Products не соответствуют активным заказам"
        )


def preflight_material_tokens_are_valid(conn):
    products = conn.execute(
        "SELECT id, name, materials FROM products ORDER BY id"
    ).fetchall()

    invalid_products = []

    for product in products:
        material_names = [
            material.strip() for material in product["materials"].split(",")
        ]

        if any(not material for material in material_names):
            invalid_products.append(product)

    if invalid_products:
        raise ValueError("Preflight failed: найдены некорректно записанные материалы")


BACKFILL_TARGET_TABLES = (
    "works",
    "materials",
    "work_images",
    "work_categories",
    "work_tags",
    "work_materials",
)


def preflight_backfill_targets_are_empty(conn):
    nonempty_tables = {}

    for table_name in BACKFILL_TARGET_TABLES:
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

        if row_count > 0:
            nonempty_tables[table_name] = row_count

    if nonempty_tables:
        raise ValueError(
            "Preflight failed: целевые таблицы backfill уже содержат данные"
        )


MATERIAL_ALIASES = {
    "каменная масса": {"name": "Каменная масса", "slug": "stoneware"},
    "фарфор": {"name": "Фарфор", "slug": "porcelain"},
    "глазурь": {"name": "Глазурь", "slug": "glaze"},
}


def preflight_material_tokens_are_known(conn):
    products = conn.execute(
        "SELECT id, name, materials FROM products ORDER BY id"
    ).fetchall()

    unknown_materials = []

    for product in products:
        material_tokens = product["materials"].split(",")

        for token in material_tokens:
            normalized_token = token.strip().lower()

            if not normalized_token:
                continue

            if normalized_token not in MATERIAL_ALIASES:
                unknown_materials.append(
                    (product["id"], product["name"], token.strip())
                )

    if unknown_materials:
        raise ValueError("Preflight failed: найдены неизвестные материалы")
