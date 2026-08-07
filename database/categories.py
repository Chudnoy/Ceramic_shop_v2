from database.connection import get_db_connection


def create_category(conn, name, slug, description):
    cursor = conn.execute(
        "INSERT INTO categories (name, slug, description) VALUES (?, ?, ?)",
        (name, slug, description),
    )

    return cursor.lastrowid


def update_category(conn, name, slug, description, category_id):
    cursor = conn.execute(
        """ UPDATE categories
                 SET name = ?, slug = ?, description = ?
                 WHERE id = ?""",
        (name, slug, description, category_id),
    )

    return cursor.rowcount > 0


def get_product_count_by_category_id(conn, category_id):
    return conn.execute(
        "SELECT COUNT(*) FROM products WHERE category_id = ?", (category_id,)
    ).fetchone()[0]


def delete_category(conn, category_id):
    cursor = conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    return cursor.rowcount > 0


def get_all_categories():
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    conn.close()
    return categories


def find_category_by_name(conn, name):
    return conn.execute(
        "SELECT * FROM categories WHERE name = ?",
        (name,),
    ).fetchone()


def find_category_by_slug(conn, slug):
    return conn.execute(
        "SELECT * FROM categories WHERE slug = ?",
        (slug,),
    ).fetchone()


def get_category_by_slug(slug):
    conn = None

    try:
        conn = get_db_connection()
        return find_category_by_slug(conn, slug)
    finally:
        if conn is not None:
            conn.close()


def get_category_by_name(name):
    conn = None

    try:
        conn = get_db_connection()
        return find_category_by_name(conn, name)
    finally:
        if conn is not None:
            conn.close()


def get_category_by_id(category_id):
    conn = get_db_connection()
    category = conn.execute(
        "SELECT * FROM categories WHERE id = ?", (category_id,)
    ).fetchone()
    conn.close()

    return category


def get_all_categories_with_product_count():
    conn = get_db_connection()
    categories = conn.execute("""SELECT categories.*, COUNT(products.id) AS products_count
                              FROM categories
                              LEFT JOIN products
                              ON products.category_id = categories.id
                              GROUP BY categories.id
                              ORDER BY categories.name""").fetchall()
    conn.close()
    return categories
