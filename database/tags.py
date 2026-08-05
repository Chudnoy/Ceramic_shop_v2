from database.connection import get_db_connection


def create_tag(tag_name, tag_slug):
    conn = get_db_connection()
    conn.execute("INSERT INTO tags (name, slug) VALUES (?, ?)", (tag_name, tag_slug))
    conn.commit()
    conn.close()


def update_tag(tag_name, tag_slug, tag_id):
    conn = get_db_connection()
    conn.execute("UPDATE tags SET name = ?, slug = ? WHERE id = ?", (tag_name, tag_slug, tag_id))
    conn.commit()
    conn.close()


def delete_tag_by_id(tag_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
    conn.commit()
    conn.close()
    
    
def get_all_tags():
    """
    Возвращает все теги, отсортированные по названию
    """
    conn = get_db_connection()
    tags = conn.execute("SELECT * FROM tags ORDER BY name").fetchall()
    conn.close()
    return tags
    
    
def get_tag_by_slug(tag_slug):
    conn = get_db_connection()
    tag = conn.execute("SELECT * FROM tags WHERE slug = ?", (tag_slug,)).fetchone()
    conn.close()
    return tag


def get_tag_by_id(tag_id):
    conn = get_db_connection()
    tag = conn.execute("SELECT * FROM tags WHERE id = ?", (tag_id,)).fetchone()
    conn.close()
    return tag
    
    
def add_tag_to_product(product_id, tag_id):
    """
    Связывает работу с тегом
    """
    conn = get_db_connection()
    conn.execute("INSERT OR IGNORE INTO product_tags (product_id, tag_id) VALUES (?, ?)", (product_id, tag_id))
    conn.commit()
    conn.close()
    
    
def replace_product_tags(conn, product_id, tag_ids):
    conn.execute("DELETE FROM product_tags WHERE product_id = ?", (product_id,))
    
    for tag_id in tag_ids:
        conn.execute("INSERT OR IGNORE INTO product_tags (product_id, tag_id) VALUES (?, ?)", (product_id, tag_id))
    
    
def get_tags_for_product(product_id):
    """
    Возвращает теги, связанные с конкретной работой.
    """
    conn = get_db_connection()
    tags = conn.execute("""
    SELECT tags.*
    FROM product_tags
    JOIN tags
    ON tags.id = product_tags.tag_id
    WHERE product_tags.product_id = ?
    ORDER BY tags.name
    """, (product_id,)).fetchall()
    
    conn.close()
    return tags
    
    
def get_tags_with_product_count():
    conn = get_db_connection()
    tags = conn.execute("""SELECT tags.*, COUNT(products.id) AS products_count
                          FROM tags
                          LEFT JOIN product_tags
                          ON product_tags.tag_id = tags.id
                          LEFT JOIN products
                          ON products.id = product_tags.product_id
                          GROUP BY tags.id
                          ORDER BY tags.name
                          """).fetchall()
    conn.close()
    return tags


def get_product_count_by_tag_id(tag_id):
    conn = get_db_connection()
    products_count = conn.execute("""SELECT COUNT(products.id)
                                  FROM tags
                                  JOIN product_tags
                                  ON product_tags.tag_id = tags.id
                                  JOIN products
                                  ON products.id = product_tags.product_id
                                  WHERE tags.id = ?""", (tag_id,)).fetchone()[0]
    conn.close()
    return products_count