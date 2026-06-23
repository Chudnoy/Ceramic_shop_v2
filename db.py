import sqlite3
import uuid

def get_db_connection():
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    return conn
    
def init_db():
    conn = get_db_connection()
    conn.execute("""CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL,
    img TEXT
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
    
    cursor = conn.execute("SELECT COUNT(*) FROM products")
    
    if cursor.fetchone()[0] == 0:
        products = [
        (str(uuid.uuid4()), "Ваза голубая", "Нежная голубая ваза", 3000, "/static/img/vase.jpg"),
        (str(uuid.uuid4()), "Кружка розовая", "Детская кружка", 2000, "/static/img/mug.jpg")
        ]
        cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products)
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
    
    
def get_all_products():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
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