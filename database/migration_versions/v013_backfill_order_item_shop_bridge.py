def preflight_shop_item_bridge_is_empty(conn):
    existing = conn.execute(
        """
        SELECT
            order_id,
            product_id,
            shop_item_id
        FROM order_items
        WHERE shop_item_id IS NOT NULL
        """
    ).fetchall()

    if existing:
        raise ValueError(
            "Preflight failed: order_items.shop_item_id уже содержит данные"
        )


def preflight_active_order_items_have_matching_shop_items(conn):
    invalid_order_items = conn.execute(
        """
        SELECT
            oi.order_id,
            oi.product_id
        FROM order_items AS oi
        JOIN orders AS o
            ON o.id = oi.order_id
        WHERE o.status IN ('new', 'confirmed')
        AND NOT EXISTS (
            SELECT 1
            FROM shop_items AS si
            WHERE si.work_id = oi.product_id
        )
        """
    ).fetchall()

    if invalid_order_items:
        raise ValueError(
            "Preflight failed: активные позиции заказов без соответствующего ShopItem"
        )


def backfill_active_order_item_shop_items(conn):
    conn.execute(
        """
        UPDATE order_items
        SET shop_item_id = (
            SELECT shop_items.id
            FROM shop_items
            WHERE shop_items.work_id = order_items.product_id
        )
        WHERE order_items.order_id IN (
            SELECT orders.id
            FROM orders
            WHERE orders.status IN ('new', 'confirmed')
        )
        """
    )


def apply(conn):
    preflight_shop_item_bridge_is_empty(conn)
    preflight_active_order_items_have_matching_shop_items(conn)
    backfill_active_order_item_shop_items(conn)
