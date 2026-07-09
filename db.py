import sqlite3
import uuid
import json

def get_db_connection():
    """
Создаёт и возвращает подключение к SQLite-базе данных shop.db.

Настраивает row_factory на sqlite3.Row, чтобы строки результата можно было читать
как словари: row["name"], row["price"], row["status"]. Это упрощает работу с
данными в routes, services и шаблонах.
"""
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    return conn
    
    
def ensure_product_columns():
    conn = get_db_connection()
    
    columns = conn.execute("PRAGMA table_info(products)").fetchall()
    column_names = [column['name'] for column in columns]
    
    if "status" not in column_names:
        conn.execute("ALTER TABLE products ADD COLUMN status TEXT NOT NULL DEFAULT 'available'")
        
    if "year" not in column_names:
        conn.execute("ALTER TABLE products ADD COLUMN year INTEGER")
        
    if "materials" not in column_names:
        conn.execute("ALTER TABLE products ADD COLUMN materials TEXT NOT NULL DEFAULT 'Каменная масса'")
        
    if 'is_visible' not in column_names:
        conn.execute('ALTER TABLE products ADD COLUMN is_visible INTEGER NOT NULL DEFAULT 1')
        
    if 'is_for_sale' not in column_names:
        conn.execute('ALTER TABLE products ADD COLUMN is_for_sale INTEGER NOT NULL DEFAULT 1')
        
    conn.commit()
    
    conn.close()
    
    
    
def init_db():
    """
Создаёт основные таблицы приложения и заполняет базу стартовыми данными.

Создаёт таблицы categories, products, reviews, orders, tags и product_tags,
если они ещё не существуют. Если таблицы категорий, тегов или работ пустые,
добавляет начальные данные.

После основной инициализации запускает ensure_product_columns(),
чтобы существующая база получила новые колонки products.
"""
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
    status TEXT NOT NULL DEFAULT 'available',
    img TEXT,
    category_id INTEGER,
    year INTEGER,
    materials TEXT NOT NULL DEFAULT 'Каменная масса',
    is_visible INTEGER NOT NULL DEFAULT 1,
    is_for_sale INTEGER NOT NULL DEFAULT 1,
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
                 
    conn.execute("""CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE
    )""")
    
    conn.execute("""CREATE TABLE IF NOT EXISTS product_tags (
    product_id TEXT NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (product_id, tag_id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
    )""")
    
    cursor = conn.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        categories = [
        ("Вазы", "vases", "Вазы утилитарные "),
        ("Кружки", "mugs", "Кружки для разных целей"),
        ("Тарелки", "plates", "Авторские тарелки для сервировки"),
        ("Чашки", "cups", "Изысканные чашки для особых моментов"),
        ("Объекты", "objects", "Объекты для интерьера")
        ]
        conn.executemany("INSERT INTO categories (name, slug, description) VALUES (?, ?, ?)", categories)
        
    cursor = conn.execute("SELECT COUNT(*) FROM tags")
    
    if cursor.fetchone()[0] == 0:
        tags = [
        ("Дом", "home"),
        ("Память", "memory"),
        ("Архитектура", "architecture"),
        ("Разрушение", "destruction"),
        ("Хрупкость", "fragility")
        ]
        
        conn.executemany("INSERT INTO tags (name, slug) VALUES (?, ?)", tags)
    
    cursor = conn.execute("SELECT COUNT(*) FROM products")
    
    if cursor.fetchone()[0] == 0:
        products = [
        (str(uuid.uuid4()), "Башня", "Тема дома красной нитью проходит сквозь всёмоё твочество. Он был разным, в зависимостиот моего состояния и меняющегося во временимира. Сейчас, я вдохновляюсь архитектуройсоветского постмодернизма, так как чувствуюсвязь, между происходящим сейчас итогда.Так я чувствую дом сейчас : какоборонительную башню, сохраняющуюхрупкость гнезда", 30000, "/static/img/tower.jpg", 5, 2025, "Каменная масса, глазури, фарфор"),
        (str(uuid.uuid4()), "Проект «Дом», Версия 3", "Этот проект — о том, как личное становится общим, а прошлое превращается в часть настоящего. Для меня тема дома всегда была лакмусовой бумажкой. Во времена спокойствия — это убежище, кокон. Во времена перемен — хрупкая раковина. В его стенах, даже воображаемых, можно увидеть и мое собственное состояние, и эхо внешнегомира.", 25000, "/static/img/dom_v3.jpg", 5, 2025, "Каменная масса, фарфор, глазури"),
        (str(uuid.uuid4()), "Сны Карелии", "Мы привыкли думать, что камни безмолвствуютвеками.Но в каждом изгибе, в каждой прожилке сокрыта тайна природы. Это не подражание, а преображение: мягкая глина застывает в образе вулканической породы, а глазурь хранит память отом, как свет играет на дне лесного озера.Прикоснитесь — и вы почувствуете не холод камня, а тепло, которое глина навсегда сберегла в памяти огня печи.", 15000, "/static/img/dreams_of_karelia.jpg", 1, 2025, "Каменная масса, глазури"),
        (str(uuid.uuid4()), "Destruction", "Проект посвящен эстетизации разрушенияи попытке навязать хаосу систему и форму.Природные катаклизмы, взрывы бытовогогаза, постепенное тление — все эти силы,уничтожающие архитектуру, находятотражение в керамических объектах, лишьотдаленно напоминающих постройки.", 10000, "/static/img/destruction.jpg", 5, 2025, "Каменная масса, фарфор, глазури"),
        (str(uuid.uuid4()), "Пасхальный купол", "Объект синтезирует архаичную символику яйца и древнерусской архитектуры. Форма яйца — универсальный архетип зарождения жизни. Венчающая часть в виде купола с нитевидной фактурой отсылает кправославным луковичным главам,символизирующим пламя свечи и небесную сферу. Цветовая гаммаимитирует пигменты народных промыслов, а белая кракелюрная глазурь напоминает глазурь на пасхальном куличе. Этаскульптура — размышление о циклическом бытии: яйцо таит в себе потенциал, купол оберегает — вместе они воплощаютнепрерывное возрождение в хаосе жизни", 17000, "/static/img/easter_dome.jpg", 1, 2025, "Каменная масса, глазури, фарфор")
        ]
        conn.executemany("INSERT INTO products (id, name, description, price, img, category_id, year, materials) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", products)
    conn.commit()
    conn.close()
    
    ensure_product_columns()
    
    
def get_all_tags():
    """
    Возвращает все теги, отсортированные по названию
    """
    conn = get_db_connection()
    tags = conn.execute("SELECT * FROM tags ORDER BY name").fetchall()
    conn.close()
    return tags
    
    
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
    
    
def get_products_by_tag_slug(tag_slug, only_visible=True):
    """
    Возвращает работы, связанные с тегом по его slug.
    """
    conn = get_db_connection()
    
    query = """
    SELECT products.*, categories.name AS category_name, categories.slug AS category_slug
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
        query += " AND products.is_visible = 1"
        
    query += " ORDER BY products.name"
    
    products = conn.execute(query, params).fetchall()
    conn.close()
    return products
    
    
def get_tag_by_slug(tag_slug):
    conn = get_db_connection()
    tag = conn.execute("SELECT * FROM tags WHERE slug = ?", (tag_slug,)).fetchone()
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
    
    
def update_product_tags(product_id, tag_ids):
    """
    Обновляет набор тегов для работы.

    Сначала удаляет старые связи работы с тегами,
    затем создаёт новые связи по переданному списку tag_ids.
    """
    conn = get_db_connection()
    conn.execute("DELETE FROM product_tags WHERE product_id = ?", (product_id,))
    
    for tag_id in tag_ids:
        conn.execute("INSERT OR IGNORE INTO product_tags (product_id, tag_id) VALUES (?, ?)", (product_id, tag_id))
    conn.commit()
    conn.close()
    
    
def get_reviews_by_product(product_id):
    """
Возвращает все отзывы для указанного товара.

Принимает product_id, ищет связанные с ним записи в таблице reviews и возвращает
их в порядке от новых к старым. Используется на странице товара для вывода блока
отзывов.
"""
    conn = get_db_connection()
    reviews = conn.execute("SELECT * FROM reviews WHERE product_id = ? ORDER BY created_at DESC", (product_id,)).fetchall()
    conn.close()
    return reviews
    
    
def add_review_db(product_id, name, rating, comment):
    """
Добавляет новый отзыв к товару в таблицу reviews.

Принимает id товара, имя автора, оценку и текст комментария. Функция предполагает,
что данные уже прошли валидацию до вызова, и только сохраняет их в базу данных.
"""
    conn = get_db_connection()
    conn.execute("INSERT INTO reviews (product_id, name, rating, comment) VALUES (?, ?, ?, ?)", (product_id, name, rating, comment))
    conn.commit()
    conn.close()
    
    
def get_all_products(
    category_slug=None,
    sort_by="name",
    order="ASC",
    search_query="",
    status="",
    only_visible=True
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
    query = f"SELECT id, name, description, price, status, img, category_id, year, materials, is_visible, is_for_sale FROM products WHERE id IN ({placeholders})"
    products = conn.execute(query, product_ids).fetchall()
    conn.close()
    return products
    
    
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

    
def delete_product(product_id):
    """
Удаляет товар из таблицы products по его id.

Функция удаляет только запись товара из базы данных. Удаление связанного файла
изображения выполняется отдельно на уровне admin route через image_service.
"""
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    
    
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

    processing_orders_count = conn.execute('SELECT COUNT(*) FROM orders WHERE status = ?', ('processing',)).fetchone()[0]

    completed_revenue = conn.execute('SELECT COALESCE(SUM(total), 0) FROM orders WHERE status = ?', ('completed',)).fetchone()[0]

    total_revenue = conn.execute('SELECT COALESCE(SUM(total), 0) FROM orders').fetchone()[0]

    conn.close()

    return {
        'products_count': products_count,
        'orders_count': orders_count,
        'new_orders_count': new_orders_count,
        'processing_orders_count': processing_orders_count,
        'completed_revenue': completed_revenue,
        'total_revenue': total_revenue
    }


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
    

def delete_category(category_id):
    """
    Удаляет категорию из базы данных, если к ней не привязаны товары.

    Сначала считает количество товаров с указанным category_id.
    Если таких товаров нет, удаляет категорию и возвращает True.
    Если в категории есть товары, не удаляет категорию и возвращает False.
    """
    conn = get_db_connection()
    products_count = conn.execute('''SELECT COUNT(*) FROM products WHERE products.category_id = ?''', (category_id,)).fetchone()[0]
    is_deleted = False
    if products_count == 0:
        conn.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        is_deleted = True
    conn.commit()
    conn.close()
    return is_deleted
    

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