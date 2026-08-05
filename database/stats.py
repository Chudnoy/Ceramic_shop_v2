from database.connection import get_db_connection


def get_admin_stats():
    """
Собирает основные статистические показатели для главной страницы админки.

Возвращает количество товаров, общее количество заказов, количество новых заказов,
количество заказов в работе, выручку по выполненным заказам и общую сумму всех
заказов. Использует COALESCE, чтобы при отсутствии заказов сумма возвращалась как 0.
"""
    conn = get_db_connection()

    products_count = conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]

    orders_count = conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]

    new_orders_count = conn.execute('SELECT COUNT(*) FROM orders WHERE status = ?', ('new',)).fetchone()[0]

    confirmed_orders_count = conn.execute("SELECT COUNT(*) FROM orders WHERE status = ?",("confirmed",)).fetchone()[0]

    completed_revenue = conn.execute('SELECT COALESCE(SUM(total), 0) FROM orders WHERE status = ?', ('completed',)).fetchone()[0]

    total_revenue = conn.execute('SELECT COALESCE(SUM(total), 0) FROM orders').fetchone()[0]

    conn.close()

    return {
        'products_count': products_count,
        'orders_count': orders_count,
        'new_orders_count': new_orders_count,
        "confirmed_orders_count": confirmed_orders_count,
        'completed_revenue': completed_revenue,
        'total_revenue': total_revenue
    }