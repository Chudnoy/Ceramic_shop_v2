def insert_order_item(
        conn,
        order_id,
        product_id,
        product_name,
        unit_price,
        quantity
):
    cursor = conn.execute(
            """
            INSERT INTO order_items (order_id, product_id, product_name, unit_price, quantity)
            VALUES (?, ?, ?, ?, ?)
            """,
            (order_id, product_id, product_name, unit_price, quantity)
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
            quantity=item["quantity"]
        )
        item_ids.append(item_id)
        
    return item_ids