import uuid

from database.connection import get_db_connection
from database.migrations import MIGRATIONS, run_migrations


def seed_artistic_demo_data(conn):
    work_count = conn.execute("SELECT COUNT(*) FROM works").fetchone()[0]

    if work_count != 0:
        return

    conn.execute(
        """
        INSERT INTO works
            (id, name, description, year, is_published)
        SELECT
            id,
            name,
            description,
            year,
            CASE
                WHEN is_visible = 1
                    AND is_archived = 0
                THEN 1
                ELSE 0
            END
        FROM products
        """
    )

    conn.execute(
        """
        INSERT INTO work_images
            (work_id, image_path, position)
        SELECT
            id,
            img,
            1
        FROM products
        WHERE img IS NOT NULL
            AND TRIM(img) != ''
        """
    )

    conn.execute(
        """
        INSERT INTO work_categories
            (work_id, category_id)
        SELECT id, category_id
        FROM products
        WHERE category_id IS NOT NULL
        """
    )

    products = conn.execute("SELECT id, materials FROM products ORDER BY id").fetchall()

    for product in products:
        material_names = [
            material.strip() for material in product["materials"].split(",")
        ]

        for material_name in material_names:
            material = conn.execute(
                "SELECT id FROM materials WHERE name = ?", (material_name,)
            ).fetchone()

            if material is None:
                raise RuntimeError(f"Seed material is not canonical: {material_name}")

            conn.execute(
                "INSERT INTO work_materials (work_id, material_id) VALUES (?, ?)",
                (product["id"], material["id"]),
            )

    conn.execute(
        """
        INSERT INTO work_tags
            (work_id, tag_id)
        SELECT
            product_id, tag_id
        FROM product_tags
        """
    )


def seed_demo_work_images(conn):
    demo_works = [
        {
            "legacy_name": "Башня",
            "name": "Капля",
            "slug": "kaplya",
            "dimensions": "24 × 24 × 18 см",
            "images": [
                "/static/uploads/works/work-01/01-cover.png",
                "/static/uploads/works/work-01/02-detail.png",
                "/static/uploads/works/work-01/03-alt.png",
                "/static/uploads/works/work-01/04-context.png",
            ],
        },
        {
            "legacy_name": "Проект «Дом». Версия 3",
            "name": "Низкая чаша",
            "slug": "nizkaya-chasha",
            "dimensions": "20 × 15 × 10 см",
            "images": [
                "/static/uploads/works/work-02/01-cover.png",
                "/static/uploads/works/work-02/02-detail.png",
                "/static/uploads/works/work-02/03-alt.png",
                "/static/uploads/works/work-02/04-context.png",
            ],
        },
        {
            "legacy_name": "Сны Карелии",
            "name": "Колонна",
            "slug": "kolonna",
            "dimensions": "24 × 24 × 18 см",
            "images": [
                "/static/uploads/works/work-03/01-cover.png",
                "/static/uploads/works/work-03/02-detail.png",
                "/static/uploads/works/work-03/03-alt.png",
                "/static/uploads/works/work-03/04-context.png",
            ],
        },
        {
            "legacy_name": "Destruction",
            "name": "Белая чаша",
            "slug": "belaya-chasha",
            "dimensions": "12 × 21 × 18 см",
            "images": [
                "/static/uploads/works/work-04/01-cover.png",
                "/static/uploads/works/work-04/02-detail.png",
                "/static/uploads/works/work-04/03-alt.png",
                "/static/uploads/works/work-04/04-context.png",
            ],
        },
        {
            "legacy_name": "Пасхальный купол",
            "name": "Кружка",
            "slug": "kruzhka",
            "dimensions": "24 × 24 × 18 см",
            "images": [
                "/static/uploads/works/work-05/01-cover.png",
                "/static/uploads/works/work-05/02-detail.png",
                "/static/uploads/works/work-05/03-alt.png",
            ],
        },
    ]

    for demo_work in demo_works:
        work = conn.execute(
            "SELECT id FROM works WHERE name in (?, ?)",
            (demo_work["legacy_name"], demo_work["name"]),
        ).fetchone()

        if work is None:
            raise RuntimeError(
                f"Demo work not found: {demo_work['legacy_name']} / {demo_work['name']}"
            )

        conn.execute(
            "UPDATE works SET name = ?, slug = ?, dimensions = ? WHERE id = ?",
            (demo_work["name"], demo_work["slug"], demo_work["dimensions"], work["id"]),
        )

        conn.execute("DELETE FROM work_images WHERE work_id = ?", (work["id"],))

        for position, image_path in enumerate(demo_work["images"], start=1):
            conn.execute(
                "INSERT INTO work_images (work_id, image_path, position) VALUES (?, ?, ?)",
                (work["id"], image_path, position),
            )


def seed_shop_demo_data(conn):
    shop_item_count = conn.execute("SELECT COUNT(*) FROM shop_items").fetchone()[0]

    if shop_item_count != 0:
        return

    products = conn.execute(
        """
        SELECT
            id, price, is_visible, is_for_sale
        FROM products
        WHERE status = 'available'
            AND is_for_sale = 1
            AND is_archived = 0
        ORDER BY id
        """
    ).fetchall()

    for product in products:
        conn.execute(
            """
            INSERT INTO shop_items
                (id, work_id, price, inventory_type, stock_quantity, is_published, is_orderable, is_retired)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                product["id"],
                product["price"],
                "unique",
                1,
                product["is_visible"] * product["is_for_sale"],
                product["is_for_sale"],
                0,
            ),
        )


def seed_initial_data():
    conn = get_db_connection()

    cursor = conn.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        categories = [
            ("Вазы", "vases", "Вазы утилитарные "),
            ("Кружки", "mugs", "Кружки для разных целей"),
            ("Тарелки", "plates", "Авторские тарелки для сервировки"),
            ("Чашки", "cups", "Изысканные чашки для особых моментов"),
            ("Объекты", "objects", "Объекты для интерьера"),
        ]
        conn.executemany(
            "INSERT INTO categories (name, slug, description) VALUES (?, ?, ?)",
            categories,
        )

    cursor = conn.execute("SELECT COUNT(*) FROM tags")

    if cursor.fetchone()[0] == 0:
        tags = [
            ("Дом", "home"),
            ("Память", "memory"),
            ("Архитектура", "architecture"),
            ("Разрушение", "destruction"),
            ("Хрупкость", "fragility"),
            ("Природа", "nature"),
        ]

        conn.executemany("INSERT INTO tags (name, slug) VALUES (?, ?)", tags)

    cursor = conn.execute("SELECT COUNT(*) FROM products")

    if cursor.fetchone()[0] == 0:
        products = [
            (
                str(uuid.uuid4()),
                "Башня",
                "Тема дома красной нитью проходит сквозь всёмоё твочество. Он был разным, в зависимостиот моего состояния и меняющегося во временимира. Сейчас, я вдохновляюсь архитектуройсоветского постмодернизма, так как чувствуюсвязь, между происходящим сейчас итогда.Так я чувствую дом сейчас : какоборонительную башню, сохраняющуюхрупкость гнезда",
                30000,
                "/static/img/tower.jpg",
                5,
                2025,
                "Каменная масса, Глазурь, Фарфор",
            ),
            (
                str(uuid.uuid4()),
                "Проект «Дом». Версия 3",
                "Этот проект — о том, как личное становится общим, а прошлое превращается в часть настоящего. Для меня тема дома всегда была лакмусовой бумажкой. Во времена спокойствия — это убежище, кокон. Во времена перемен — хрупкая раковина. В его стенах, даже воображаемых, можно увидеть и мое собственное состояние, и эхо внешнегомира.",
                25000,
                "/static/img/dom_v3.jpg",
                5,
                2025,
                "Каменная масса, Фарфор, Глазурь",
            ),
            (
                str(uuid.uuid4()),
                "Сны Карелии",
                "Мы привыкли думать, что камни безмолвствуютвеками.Но в каждом изгибе, в каждой прожилке сокрыта тайна природы. Это не подражание, а преображение: мягкая глина застывает в образе вулканической породы, а глазурь хранит память отом, как свет играет на дне лесного озера.Прикоснитесь — и вы почувствуете не холод камня, а тепло, которое глина навсегда сберегла в памяти огня печи.",
                15000,
                "/static/img/dreams_of_karelia.jpg",
                1,
                2025,
                "Каменная масса, Глазурь",
            ),
            (
                str(uuid.uuid4()),
                "Destruction",
                "Проект посвящен эстетизации разрушенияи попытке навязать хаосу систему и форму.Природные катаклизмы, взрывы бытовогогаза, постепенное тление — все эти силы,уничтожающие архитектуру, находятотражение в керамических объектах, лишьотдаленно напоминающих постройки.",
                10000,
                "/static/img/destruction.jpg",
                5,
                2025,
                "Каменная масса, Фарфор, Глазурь",
            ),
            (
                str(uuid.uuid4()),
                "Пасхальный купол",
                "Объект синтезирует архаичную символику яйца и древнерусской архитектуры. Форма яйца — универсальный архетип зарождения жизни. Венчающая часть в виде купола с нитевидной фактурой отсылает кправославным луковичным главам,символизирующим пламя свечи и небесную сферу. Цветовая гаммаимитирует пигменты народных промыслов, а белая кракелюрная глазурь напоминает глазурь на пасхальном куличе. Этаскульптура — размышление о циклическом бытии: яйцо таит в себе потенциал, купол оберегает — вместе они воплощаютнепрерывное возрождение в хаосе жизни",
                17000,
                "/static/img/easter_dome.jpg",
                1,
                2025,
                "Каменная масса, Глазурь, Фарфор",
            ),
        ]
        conn.executemany(
            "INSERT INTO products (id, name, description, price, img, category_id, year, materials) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            products,
        )

    seed_artistic_demo_data(conn)
    seed_demo_work_images(conn)
    seed_shop_demo_data(conn)

    conn.commit()
    conn.close()


def init_db():
    conn = get_db_connection()

    try:
        run_migrations(conn=conn, available_migrations=MIGRATIONS)
    finally:
        conn.close()

    seed_initial_data()
