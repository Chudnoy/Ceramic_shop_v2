def insert_order_item(conn, order_id, product_id, product_name, unit_price, quantity):
    cursor = conn.execute(
        """
            INSERT INTO order_items (order_id, product_id, product_name, unit_price, quantity)
            VALUES (?, ?, ?, ?, ?)
            """,
        (order_id, product_id, product_name, unit_price, quantity),
    )

    return cursor.lastrowid


def insert_order_items(conn, order_id, items):
    item_ids = []

    for item in items:
        item_id = insert_order_item(
            conn=conn,
            order_id=order_id,
            product_id=item["product_id"],
            product_name=item["product_name"],
            unit_price=item["unit_price"],
            quantity=item["quantity"],
        )
        item_ids.append(item_id)

    return item_ids


def get_order_items_by_order_id(conn, order_id):
    items = conn.execute(
        """
                 SELECT
                 id, order_id, product_id, product_name, unit_price, quantity
                 FROM order_items
                 WHERE order_id = ? ORDER BY id
                 """,
        (order_id,),
    ).fetchall()
    return items


def update_order_item_quantity(conn, order_id, item_id, quantity):
    cursor = conn.execute(
        """
        UPDATE order_items
        SET quantity = ?
        WHERE id = ? AND order_id = ?
        """,
        (quantity, item_id, order_id),
    )

    return cursor.rowcount > 0
