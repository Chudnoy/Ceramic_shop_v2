import json
from database.connection import get_db_connection


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
        (id, customer_name, customer_email, customer_phone, customer_address, items, total, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (order_id, customer_name, customer_email, customer_phone, customer_address, "{}", total, status)
    )


def create_order(order_id, customer_name, customer_email, customer_phone, customer_address, items_dict, total):
    """
Создаёт новый заказ в таблице orders.

Принимает данные покупателя, словарь товаров заказа и итоговую сумму. Словарь
товаров преобразуется в JSON перед сохранением в базу. Новый заказ создаётся
со статусом "new".
"""
    conn = get_db_connection()
    items_json = json.dumps(items_dict, ensure_ascii=False)
    conn.execute("""INSERT INTO orders (id, customer_name, customer_email, customer_phone, customer_address, items, total, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                 (order_id,customer_name, customer_email, customer_phone, customer_address, items_json, total, 'new'))
    conn.commit()
    conn.close()
    
    
def update_order(order_id, name, email, phone, address, items, total, status):
    """
Обновляет данные существующего заказа.

Принимает обновлённые данные покупателя, состав заказа, итоговую сумму и статус.
Словарь товаров преобразуется в JSON перед сохранением в базу данных.
"""
    conn = get_db_connection()
    items_json = json.dumps(items, ensure_ascii=False)
    conn.execute("""
    UPDATE orders
    SET customer_name = ?, customer_email = ?, customer_phone = ?, customer_address = ?, items = ?, total = ?, status = ?
    WHERE id = ?""",
    (name, email, phone, address, items_json, total, status, order_id))
    conn.commit()
    conn.close()
    
    
def delete_order(order_id):
    """
Удаляет заказ из таблицы orders по его id.

Используется в админке для удаления заказа. Функция удаляет только запись заказа
из базы данных и не изменяет товары, которые входили в заказ.
"""
    conn = get_db_connection()
    conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    
    
def get_all_orders(search_query='', status=''):
    """
Возвращает список заказов с возможной фильтрацией по поиску и статусу.

Позволяет искать заказы по id, имени покупателя, email, телефону и адресу.
Также может фильтровать заказы по статусу. Поле items каждого заказа декодируется
из JSON в Python-словарь перед возвратом.
"""
    conn = get_db_connection()
    query = 'SELECT * FROM orders'
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
    conn.close()

    orders = []

    for row in rows:
        order = dict(row)
        order['items'] = json.loads(order['items'])
        orders.append(order)
    return orders
    
    
def get_order_by_id(order_id):
    """
Возвращает заказ по его id.

Загружает заказ из таблицы orders, преобразует строку в обычный словарь и
декодирует поле items из JSON обратно в Python-словарь. Если заказ не найден,
возвращает None.
"""
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    conn.close()

    if not row:
        return None
    
    order = dict(row)
    order['items'] = json.loads(order['items'])
    return order
    
    
def update_order_status(order_id, status):
    """
Обновляет только статус заказа.

Используется для быстрого изменения статуса заказа из админского списка без
редактирования остальных данных заказа.
"""
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    conn.commit()
    conn.close()