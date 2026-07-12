import uuid
import json
from database.connection import get_db_connection


def create_product(name, price, description, img_path, category_id, status, year, materials, is_visible, is_for_sale):
    """
    Создаёт новый товар в таблице products и возвращает id созданной записи.
    """
    product_id = str(uuid.uuid4())
    conn = get_db_connection()
    conn.execute("""
    INSERT INTO products (id, name, description, price, img, category_id, status, year, materials, is_visible, is_for_sale)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
    (product_id, name, description, price, img_path, category_id, status, year, materials, is_visible, is_for_sale))
    conn.commit()
    conn.close()
    
    return product_id
    
    
def update_product(product_id, name, price, description, img_path, category_id, status, year, materials, is_visible, is_for_sale):
    """
Обновляет данные существующего товара.

Сохраняет новое название, описание, цену, категорию, путь к изображению и статус
товара. Используется в админке после успешной обработки формы редактирования.
"""
    conn = get_db_connection()
    conn.execute("""
    UPDATE products
    SET name = ?, description = ?, price = ?, category_id = ?, img = ?, status = ?, year = ?, materials = ?, is_visible = ?, is_for_sale = ?
    WHERE id = ?
    """, (name, description, price, category_id, img_path, status, year, materials, is_visible, is_for_sale, product_id))
    conn.commit()
    conn.close()
    
    
def delete_product(product_id):
    """
    Окончательно удаляет работу из базы.

    Сначала удаляет зависимые строки:
    - связи работы с тегами;
    - отзывы работы.

    Затем удаляет саму работу.

    Все изменения сохраняются одним commit().
    """
    conn = get_db_connection()

    conn.execute("DELETE FROM product_tags WHERE product_id = ?", (product_id,))

    conn.execute("DELETE FROM reviews WHERE product_id = ?", (product_id,))

    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))

    conn.commit()
    conn.close()


def product_exists(product_id):
    """
Проверяет, существует ли товар с указанным id.

Возвращает True, если в таблице products есть запись с таким id, иначе False.
Используется там, где нужно быстро проверить существование товара без загрузки
всех его данных.
"""
    conn = get_db_connection()
    product = conn.execute("SELECT 1 FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return product is not None
    

def get_all_products(
    category_slug=None,
    sort_by="name",
    order="ASC",
    search_query="",
    status="",
    only_visible=True,
    is_archived=False
):
    """
    Возвращает список работ с учётом категории, поиска, сортировки,
    статуса и публичной видимости.

    only_visible=True используется для публичной части сайта:
    показываются только опубликованные работы.

    only_visible=False используется в админке:
    показываются все работы, включая скрытые с сайта.
    """
    conn = get_db_connection()

    query = """
    SELECT products.*, categories.name AS category_name, categories.slug AS category_slug
    FROM products
    LEFT JOIN categories
    ON products.category_id = categories.id
    """

    params = []
    conditions = []
    
    if is_archived:
        conditions.append("products.is_archived = 1")
    else:
        conditions.append("products.is_archived = 0")

    if only_visible:
        conditions.append("products.is_visible = 1")

    if category_slug:
        conditions.append("categories.slug = ?")
        params.append(category_slug)

    if search_query:
        conditions.append("(products.name LIKE ? OR products.description LIKE ?)")
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    allowed_statuses = {"available", "reserved", "sold"}
    status = status.strip().lower()

    if status in allowed_statuses:
        conditions.append("products.status = ?")
        params.append(status)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    allowed_sort_fields = {
        "name": "products.name",
        "price": "products.price"
    }

    sort_field = allowed_sort_fields.get(sort_by, "products.name")

    allowed_sort_orders = ("ASC", "DESC")
    order = order.upper() if order.upper() in allowed_sort_orders else "ASC"

    query += f" ORDER BY {sort_field} {order}"

    products = conn.execute(query, params).fetchall()
    conn.close()

    return products
    
    
def get_product_by_id(product_id):
    """
Возвращает товар по его id.

Ищет одну запись в таблице products. Если товар найден, возвращает sqlite3.Row
с данными товара. Если товара нет, возвращает None.
"""
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return product
    
    
def get_products_by_ids(product_ids):
    """
Возвращает список товаров по набору id.

Используется для восстановления товаров из корзины, где в session хранятся только
id товаров и количество. Если список id пустой, сразу возвращает пустой список
без обращения к базе данных.
"""
    if not product_ids:
        return []
    conn = get_db_connection()
    placeholders = ", ".join("?" * len(product_ids))
    query = f"SELECT id, name, description, price, status, img, category_id, year, materials, is_visible, is_archived, is_for_sale FROM products WHERE id IN ({placeholders})"
    products = conn.execute(query, product_ids).fetchall()
    conn.close()
    return products
    
    
def get_product_with_category(product_id):
    """
Возвращает товар вместе с данными его категории.

Используется на странице отдельного товара, где помимо данных самого товара нужно
показать название и slug категории. Если товар не найден, возвращает None.
"""
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
    
    
def get_products_by_category(category_id):
    """
Возвращает товары указанной категории.

Принимает category_id и возвращает товары, связанные с этой категорией, вместе
с названием категории. Это более прямой вариант выборки по category_id, в отличие
от get_all_products, где фильтрация идёт через slug.
"""
    conn = get_db_connection()
    products = conn.execute("""SELECT products.*, categories.name AS category_name
    FROM products
    JOIN categories
    ON products.category_id = categories.id
    WHERE products.category_id = ?""", (category_id,)).fetchall()
    conn.close()
    return products
    
    
def get_products_by_tag_slug(tag_slug, only_visible=True):
    """
    Возвращает работы, связанные с тегом по его slug.

    Для публичной части сайта возвращает только опубликованные
    и неархивные работы.

    Для админки при only_visible=False возвращает все связанные работы,
    включая скрытые и архивные.
    """
    conn = get_db_connection()

    query = """
        SELECT
            products.*,
            categories.name AS category_name,
            categories.slug AS category_slug
        FROM tags
        JOIN product_tags
            ON tags.id = product_tags.tag_id
        JOIN products
            ON product_tags.product_id = products.id
        LEFT JOIN categories
            ON products.category_id = categories.id
        WHERE tags.slug = ?
    """

    params = [tag_slug]

    if only_visible:
        query += """
            AND products.is_visible = 1
            AND products.is_archived = 0
        """

    query += " ORDER BY products.name"

    products = conn.execute(query, params).fetchall()

    conn.close()
    return products
    
    
def set_product_archived(product_id, is_archived):
    """
    Изменяет состояние архива работы.

    is_archived:
    1 — работа находится в архиве;
    0 — работа активна.

    Функция не изменяет is_visible и is_for_sale, поэтому после восстановления
    сохраняются прежние настройки публикации и продажи.
    """
    conn = get_db_connection()

    conn.execute(
        """
        UPDATE products
        SET is_archived = ?
        WHERE id = ?
        """,
        (is_archived, product_id)
    )

    conn.commit()
    conn.close()