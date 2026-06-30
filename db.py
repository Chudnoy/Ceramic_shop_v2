import sqlite3
import uuid
import json

def get_db_connection():
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    return conn
    
def init_db():
    conn = get_db_connection()
    
    conn.execute("""CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    description TEXT
    )""")
    
    conn.execute("""CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL,
    img TEXT,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(id)
    )""")
    
    conn.execute("""CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    name TEXT NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
    )""")

    conn.execute("""CREATE TABLE IF NOT EXISTS orders (
                 id TEXT PRIMARY KEY,
                 customer_name TEXT NOT NULL,
                 customer_email TEXT NOT NULL,
                 customer_phone TEXT,
                 customer_address TEXT,
                 items TEXT NOT NULL,
                 total INTEGER NOT NULL,
                 status TEXT NOT NULL DEFAULT 'new',
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )""")
    
    cursor = conn.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        categories = [
        ("Вазы", "vases", "Красивые вазы ручной работы"),
        ("Кружки", "mugs", "Уютные кружки для чая и кофе"),
        ("Тарелки", "plates", "Авторские тарелки для сервировки"),
        ("Чашки", "cups", "Изысканные чашки для особых моментов"),
        ("Статуэтки", "figurines", "Интерьерные статуэтки разных размеров")
        ]
        conn.executemany("INSERT INTO categories (name, slug, description) VALUES (?, ?, ?)", categories)
    
    cursor = conn.execute("SELECT COUNT(*) FROM products")
    
    if cursor.fetchone()[0] == 0:
        products = [
        (str(uuid.uuid4()), "Ваза голубая", "Нежная голубая ваза", 3000, "/static/img/vase.jpeg", 1),
        (str(uuid.uuid4()), "Ваза белая", "Утонченная белая ваза", 5000, "/static/img/white_vase.jpeg", 1),
        (str(uuid.uuid4()), "Кружка розовая", "Детская кружка с сердечком", 2000, "/static/img/pink_mug.jpeg", 2),
        (str(uuid.uuid4()), "Кружка чёрная", "Строгая черная кружка", 2500, "/static/img/black_mug.jpeg", 2),
        (str(uuid.uuid4()), "Тарелка декоративная", "Тарелка с золотым узором", 4000, "/static/img/plate.jpeg", 3)
        ]
        cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)", products)
    conn.commit()
    conn.close()
    
    
def get_reviews_by_product(product_id):
    conn = get_db_connection()
    reviews = conn.execute("SELECT * FROM reviews WHERE product_id = ? ORDER BY created_at DESC", (product_id,)).fetchall()
    conn.close()
    return reviews
    
    
def add_review_db(product_id, name, rating, comment):
    conn = get_db_connection()
    conn.execute("INSERT INTO reviews (product_id, name, rating, comment) VALUES (?, ?, ?, ?)", (product_id, name, rating, comment))
    conn.commit()
    conn.close()
    
    
def get_all_products(category_slug=None, sort_by='name', order='ASC', search_query=""):
    conn = get_db_connection()
    query = """SELECT products.*, categories.name AS category_name, categories.slug AS category_slug
            FROM products
            LEFT JOIN categories
            ON products.category_id = categories.id"""
    
    params = []
    condition = []
    if category_slug:
        condition.append("categories.slug = ?")
        params.append(category_slug)
        
    if search_query:
        condition.append("(products.name LIKE ? OR products.description LIKE ?)")
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        
    if condition:
        query += " WHERE " + " AND ".join(condition)
    
    allowed_sort_fields = {'name': 'products.name', 'price': 'products.price'}
    sort_field = allowed_sort_fields.get(sort_by, 'products.name')
    allowed_sort_orders = ('ASC', 'DESC')
    order = order.upper() if order.upper() in allowed_sort_orders else 'ASC'

    query += f" ORDER BY {sort_field} {order}"
    products = conn.execute(query, params).fetchall()
    conn.close()
    return products
    
    
def get_product_by_id(product_id):
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return product
    
    
def get_products_by_ids(product_ids):
    if not product_ids:
        return []
    conn = get_db_connection()
    placeholders = ", ".join("?" * len(product_ids))
    query = f"SELECT id, name, price FROM products WHERE id IN ({placeholders})"
    products = conn.execute(query, product_ids).fetchall()
    conn.close()
    return products
    
    
def product_exists(product_id):
    conn = get_db_connection()
    product = conn.execute("SELECT 1 FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return product is not None


def create_order(order_id, customer_name, customer_email, customer_phone, customer_address, items_dict, total):
    conn = get_db_connection()
    items_json = json.dumps(items_dict, ensure_ascii=False)
    conn.execute("""INSERT INTO orders (id, customer_name, customer_email, customer_phone, customer_address, items, total, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                 (order_id,customer_name, customer_email, customer_phone, customer_address, items_json, total, 'new'))
    conn.commit()
    conn.close()


def get_order_by_id(order_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    conn.close()

    if not row:
        return None
    
    order = dict(row)
    order['items'] = json.loads(order['items'])
    return order


def get_all_orders(search_query='', status=''):
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
    
    
def get_all_categories():
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    conn.close()
    return categories
    
    
def get_category_by_slug(slug):
    conn = get_db_connection()
    category = conn.execute("SELECT * FROM categories WHERE slug = ?", (slug,)).fetchone()
    conn.close()
    return category
    
    
def get_products_by_category(category_id):
    conn = get_db_connection()
    products = conn.execute("""SELECT products.*, categories.name AS category_name
    FROM products
    JOIN categories
    ON products.category_id = categories.id
    WHERE products.category_id = ?""", (category_id,)).fetchall()
    conn.close()
    return products
    
    
def get_product_with_category(product_id):
    conn = get_db_connection()
    product = conn.execute("""SELECT 
        products.*, 
        categories.name AS category_name,
        categories.slug AS category_slug
        FROM products
        LEFT JOIN categories
        ON products.category_id = categories.id
        WHERE products.id = ?
        """, (product_id,)).fetchone()
    conn.close()
    return product
    
    
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    
    
def update_product(product_id, name, price, description, img_path, category_id):
    conn = get_db_connection()
    conn.execute("""
    UPDATE products
    SET name = ?, description = ?, price = ?, category_id = ?, img = ?
    WHERE id = ?
    """, (name, description, price, category_id, img_path, product_id))
    conn.commit()
    conn.close()
    
    
def create_product(name, price, description, img_path, category_id):
    conn = get_db_connection()
    conn.execute("""
    INSERT INTO products (id, name, description, price, img, category_id)
    VALUES (?, ?, ?, ?, ?, ?)""",
    (str(uuid.uuid4()), name, description, price, img_path, category_id))
    conn.commit()
    conn.close()
    
    
def delete_order(order_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    
    
def update_order(order_id, name, email, phone, address, items, total, status):
    conn = get_db_connection()
    items_json = json.dumps(items, ensure_ascii=False)
    conn.execute("""
    UPDATE orders
    SET customer_name = ?, customer_email = ?, customer_phone = ?, customer_address = ?, items = ?, total = ?, status = ?
    WHERE id = ?""",
    (name, email, phone, address, items_json, total, status, order_id))
    conn.commit()
    conn.close()


def update_order_status(order_id, status):
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    conn.commit()
    conn.close()