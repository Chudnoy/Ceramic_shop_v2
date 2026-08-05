import uuid
from database.connection import get_db_connection

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
        
    if "is_archived" not in column_names:
        conn.execute("ALTER TABLE products ADD COLUMN is_archived INTEGER NOT NULL DEFAULT 0")
        
    if "is_featured" not in column_names:
        conn.execute("ALTER TABLE products ADD COLUMN is_featured INTEGER NOT NULL DEFAULT 0")
        
    conn.commit()
    
    conn.close()


def create_schema():
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
        is_archived INTEGER NOT NULL DEFAULT 0,
        is_featured INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES categories(id)
        )""")
    
    conn.execute("""CREATE TABLE IF NOT EXISTS orders (
                     id TEXT PRIMARY KEY,
                     customer_name TEXT NOT NULL,
                     customer_email TEXT NOT NULL,
                     customer_phone TEXT,
                     customer_address TEXT,
                     total INTEGER NOT NULL,
                     status TEXT NOT NULL DEFAULT 'new',
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                     )""")
                     
    conn.execute("""CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                product_id TEXT,
                product_name TEXT NOT NULL,
                unit_price INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                
                FOREIGN KEY (order_id)
                    REFERENCES orders(id)
                    ON DELETE CASCADE,
                
                FOREIGN KEY (product_id)
                    REFERENCES products(id)
                    ON DELETE SET NULL
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

    conn.commit()
    conn.close()

    ensure_product_columns()


def seed_initial_data():
    conn = get_db_connection()

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
        ("Хрупкость", "fragility"),
        ("Природа", "nature")
        ]
        
        conn.executemany("INSERT INTO tags (name, slug) VALUES (?, ?)", tags)
    
    cursor = conn.execute("SELECT COUNT(*) FROM products")
    
    if cursor.fetchone()[0] == 0:
        products = [
        (str(uuid.uuid4()), "Башня", "Тема дома красной нитью проходит сквозь всёмоё твочество. Он был разным, в зависимостиот моего состояния и меняющегося во временимира. Сейчас, я вдохновляюсь архитектуройсоветского постмодернизма, так как чувствуюсвязь, между происходящим сейчас итогда.Так я чувствую дом сейчас : какоборонительную башню, сохраняющуюхрупкость гнезда", 30000, "/static/img/tower.jpg", 5, 2025, "Каменная масса, глазури, фарфор"),
        (str(uuid.uuid4()), "Проект «Дом». Версия 3", "Этот проект — о том, как личное становится общим, а прошлое превращается в часть настоящего. Для меня тема дома всегда была лакмусовой бумажкой. Во времена спокойствия — это убежище, кокон. Во времена перемен — хрупкая раковина. В его стенах, даже воображаемых, можно увидеть и мое собственное состояние, и эхо внешнегомира.", 25000, "/static/img/dom_v3.jpg", 5, 2025, "Каменная масса, фарфор, глазури"),
        (str(uuid.uuid4()), "Сны Карелии", "Мы привыкли думать, что камни безмолвствуютвеками.Но в каждом изгибе, в каждой прожилке сокрыта тайна природы. Это не подражание, а преображение: мягкая глина застывает в образе вулканической породы, а глазурь хранит память отом, как свет играет на дне лесного озера.Прикоснитесь — и вы почувствуете не холод камня, а тепло, которое глина навсегда сберегла в памяти огня печи.", 15000, "/static/img/dreams_of_karelia.jpg", 1, 2025, "Каменная масса, глазури"),
        (str(uuid.uuid4()), "Destruction", "Проект посвящен эстетизации разрушенияи попытке навязать хаосу систему и форму.Природные катаклизмы, взрывы бытовогогаза, постепенное тление — все эти силы,уничтожающие архитектуру, находятотражение в керамических объектах, лишьотдаленно напоминающих постройки.", 10000, "/static/img/destruction.jpg", 5, 2025, "Каменная масса, фарфор, глазури"),
        (str(uuid.uuid4()), "Пасхальный купол", "Объект синтезирует архаичную символику яйца и древнерусской архитектуры. Форма яйца — универсальный архетип зарождения жизни. Венчающая часть в виде купола с нитевидной фактурой отсылает кправославным луковичным главам,символизирующим пламя свечи и небесную сферу. Цветовая гаммаимитирует пигменты народных промыслов, а белая кракелюрная глазурь напоминает глазурь на пасхальном куличе. Этаскульптура — размышление о циклическом бытии: яйцо таит в себе потенциал, купол оберегает — вместе они воплощаютнепрерывное возрождение в хаосе жизни", 17000, "/static/img/easter_dome.jpg", 1, 2025, "Каменная масса, глазури, фарфор")
        ]
        conn.executemany("INSERT INTO products (id, name, description, price, img, category_id, year, materials) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", products)

    conn.commit()
    conn.close()
    
    
    
def init_db():
    create_schema()
    seed_initial_data()