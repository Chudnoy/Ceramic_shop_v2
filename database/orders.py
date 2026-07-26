from database.connection import get_db_connection
from database.order_items import get_order_items_by_order_id


def insert_order(
        conn,
        order_id,
        customer_name,
        customer_email,
        customer_phone,
        customer_address,
        total,
        status="new"
):
    conn.execute(
        """
        INSERT INTO orders
        (id, customer_name, customer_email, customer_phone, customer_address, total, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (order_id, customer_name, customer_email, customer_phone, customer_address, total, status)
    )


def update_order_details(conn, order_id, customer_name, customer_email, customer_phone, customer_address, total, expexted_status):
    cursor = conn.execute(
        """
        UPDATE orders
        SET
            customer_name = ?, customer_email = ?, customer_phone = ?, customer_address = ?, total = ?
        WHERE id = ? AND status = ?
        """,
        (customer_name, customer_email, customer_phone, customer_address, total, order_id, expexted_status)
    )

    return cursor.rowcount > 0
    
    
def delete_order(conn, order_id, exprcted_status):
    cursor = conn.execute("DELETE FROM orders WHERE id = ? AND status = ?", (order_id, exprcted_status))

    return cursor.rowcount > 0
    
    
def get_all_orders(search_query='', status=''):
    conn = None
    try:
        conn = get_db_connection()
        query = """
                SELECT
                id, customer_name, customer_email, customer_phone, total, status, created_at
                FROM orders
                """
        params = []
        condition = []

        if search_query:
            condition.append('(id LIKE ? OR customer_name LIKE ? OR customer_email LIKE ? OR customer_phone LIKE ? OR customer_address LIKE ?)')
            search_pattern = f'%{search_query}%'
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])

        if status:
            condition.append('status = ?')
            params.append(status)

        if condition:
            query += ' WHERE ' + ' AND '.join(condition)
        
        query += ' ORDER BY created_at DESC'

        rows = conn.execute(query, params).fetchall()

        return [dict(row) for row in rows]
    finally:
        if conn is not None:
            conn.close()
    
    
def get_order_by_id(order_id):
    conn = None
    try:
        conn = get_db_connection()
        order_row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()

        if order_row is None:
            return None
        
        order = dict(order_row)

        saved_items = get_order_items_by_order_id(conn=conn, order_id=order_id)

        order['items'] =[dict(item) for item in saved_items]

        return order
    
    finally:
        if conn is not None:
            conn.close()
    
    
def update_order_status(conn, order_id, new_status, expected_status):
    cursor = conn.execute("UPDATE orders SET status = ? WHERE id = ? AND status = ?", (new_status, order_id, expected_status))
    
    return cursor.rowcount > 0


def has_active_order_for_product(conn, product_id):
    active_order = conn.execute(
        """
        SELECT 1
        FROM order_items
        JOIN orders
            ON orders.id = order_items.order_id
        WHERE order_items.product_id = ?
          AND orders.status IN ('new', 'confirmed')
        LIMIT 1
        """,
        (product_id,)
    ).fetchone()

    return active_order is not None