from database.connection import get_db_connection


def create_category(name, slug, description):
    """
    Создаёт новую категорию в базе данных.

    Принимает название, slug и описание категории, добавляет новую запись
    в таблицу categories и сохраняет изменения.
    """
    conn = get_db_connection()
    conn.execute('INSERT INTO categories (name, slug, description) VALUES (?, ?, ?)',
                 (name, slug, description))
    conn.commit()
    conn.close()
    
    
def update_category(name, new_slug, description, slug):
    """
    Обновляет данные существующей категории.

    Находит категорию по её текущему slug и обновляет название, slug
    и описание. Используется при редактировании категории в админке.
    """
    conn = get_db_connection()
    conn.execute(''' UPDATE categories
                 SET name = ?, slug = ?, description = ?
                 WHERE slug = ?''',
                 (name, new_slug, description, slug))
    conn.commit()
    conn.close()
    
    
def delete_category(category_id):
    """
    Удаляет категорию из базы данных, если к ней не привязаны товары.

    Сначала считает количество товаров с указанным category_id.
    Если таких товаров нет, удаляет категорию и возвращает True.
    Если в категории есть товары, не удаляет категорию и возвращает False.
    """
    conn = get_db_connection()
    
    try:
        products_count = conn.execute("SELECT COUNT(*) FROM products WHERE category_id = ?", (category_id,)).fetchone()[0]
        
        if products_count > 0:
            return False
        
        cursor = conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    
    
def get_all_categories():
    """
Возвращает все категории товаров.

Загружает категории из таблицы categories и сортирует их по названию. Используется
в каталоге, админских фильтрах и формах создания или редактирования товара.
"""
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    conn.close()
    return categories
    
    
def get_category_by_slug(slug):
    """
Возвращает категорию по её slug.

Используется при фильтрации каталога или админского списка товаров по категории.
Если категория с таким slug не найдена, возвращает None.
"""
    conn = get_db_connection()
    category = conn.execute("SELECT * FROM categories WHERE slug = ?", (slug,)).fetchone()
    conn.close()
    return category
    
    
def get_category_by_id(category_id):
    conn = get_db_connection()
    category = conn.execute("SELECT * FROM categories WHERE id = ?", (category_id,)).fetchone()
    conn.close()
    
    return category
    
    
def get_all_categories_with_product_count():
    conn = get_db_connection()
    categories = conn.execute('''SELECT categories.*, COUNT(products.id) AS products_count
                              FROM categories
                              LEFT JOIN products
                              ON products.category_id = categories.id
                              GROUP BY categories.id
                              ORDER BY categories.name''').fetchall()
    conn.close()
    return categories