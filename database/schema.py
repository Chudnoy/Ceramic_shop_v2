from database.connection import get_db_connection
from database.migrations import MIGRATIONS, run_migrations

KAPLYA_ID = "f05b463a-5d51-4c2b-8922-2fc38fcda0bf"
NIZKAYA_CHASHA_ID = "d40d7b3e-0621-421b-8681-f85bdb7db392"
KOLONNA_ID = "7e87e224-3962-4717-850f-36442ac0132d"
BELAYA_CHASHA_ID = "21f813a5-cf21-4fa8-89e3-21879895c0d5"
KRUZHKA_ID = "ab37a435-afb9-4dea-b8a9-4ce47e5e268f"


def seed_initial_data():
    conn = get_db_connection()

    try:
        work_count = conn.execute("SELECT COUNT(*) FROM works").fetchone()[0]

        if work_count != 0:
            return

        categories = [
            ("Вазы", "vases", "Вазы и сосуды"),
            ("Кружки", "mugs", "Кружки и утилитарные формы"),
            ("Тарелки", "plates", "Тарелки и плоские формы"),
            ("Чаши", "bowls", "Чаши и открытые формы"),
            ("Объекты", "objects", "Скульптурные и интерьерные объекты"),
        ]

        conn.executemany(
            """
            INSERT INTO categories (
                name,
                slug,
                description
            )
            VALUES (?, ?, ?)
            """,
            categories,
        )

        tags = [
            ("Дом", "home"),
            ("Память", "memory"),
            ("Архитектура", "architecture"),
            ("Разрушение", "destruction"),
            ("Хрупкость", "fragility"),
            ("Природа", "nature"),
        ]

        conn.executemany(
            """
            INSERT INTO tags (
                name,
                slug
            )
            VALUES (?, ?)
            """,
            tags,
        )

        works = [
            (
                KAPLYA_ID,
                "kaplya",
                "Капля",
                (
                    "Скульптурный керамический объект с пористой "
                    "структурой и вытянутым силуэтом."
                ),
                2025,
                "24 × 24 × 18 см",
                None,
                None,
                None,
                1,
                0,
                None,
            ),
            (
                NIZKAYA_CHASHA_ID,
                "nizkaya-chasha",
                "Низкая чаша",
                ("Низкая открытая форма с выраженной фактурой поверхности."),
                2025,
                "20 × 15 × 10 см",
                None,
                None,
                None,
                1,
                0,
                None,
            ),
            (
                KOLONNA_ID,
                "kolonna",
                "Колонна",
                (
                    "Высокий керамический объект, построенный "
                    "на ритме отверстий и повторяющейся фактуры."
                ),
                2025,
                "24 × 24 × 18 см",
                None,
                None,
                None,
                1,
                0,
                None,
            ),
            (
                BELAYA_CHASHA_ID,
                "belaya-chasha",
                "Белая чаша",
                (
                    "Чаша со светлой поверхностью и подчёркнутой "
                    "нерегулярностью ручной формы."
                ),
                2025,
                "12 × 21 × 18 см",
                None,
                None,
                None,
                1,
                1,
                "Возможно изготовление близкой работы по запросу.",
            ),
            (
                KRUZHKA_ID,
                "kruzhka",
                "Кружка",
                ("Утилитарная керамическая форма с рельефной поверхностью."),
                2025,
                "12 × 9 × 9 см",
                None,
                None,
                None,
                1,
                0,
                None,
            ),
        ]

        conn.executemany(
            """
            INSERT INTO works (
                id,
                slug,
                name,
                description,
                year,
                dimensions,
                project_id,
                series_id,
                project_position,
                is_published,
                is_commissionable,
                commission_note
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            works,
        )

        work_images = [
            (
                KAPLYA_ID,
                "/static/uploads/works/work-01/01-cover.png",
                1,
            ),
            (
                KAPLYA_ID,
                "/static/uploads/works/work-01/02-detail.png",
                2,
            ),
            (
                KAPLYA_ID,
                "/static/uploads/works/work-01/03-alt.png",
                3,
            ),
            (
                KAPLYA_ID,
                "/static/uploads/works/work-01/04-context.png",
                4,
            ),
            (
                NIZKAYA_CHASHA_ID,
                "/static/uploads/works/work-02/01-cover.png",
                1,
            ),
            (
                NIZKAYA_CHASHA_ID,
                "/static/uploads/works/work-02/02-detail.png",
                2,
            ),
            (
                NIZKAYA_CHASHA_ID,
                "/static/uploads/works/work-02/03-alt.png",
                3,
            ),
            (
                NIZKAYA_CHASHA_ID,
                "/static/uploads/works/work-02/04-context.png",
                4,
            ),
            (
                KOLONNA_ID,
                "/static/uploads/works/work-03/01-cover.png",
                1,
            ),
            (
                KOLONNA_ID,
                "/static/uploads/works/work-03/02-detail.png",
                2,
            ),
            (
                KOLONNA_ID,
                "/static/uploads/works/work-03/03-alt.png",
                3,
            ),
            (
                KOLONNA_ID,
                "/static/uploads/works/work-03/04-context.png",
                4,
            ),
            (
                BELAYA_CHASHA_ID,
                "/static/uploads/works/work-04/01-cover.png",
                1,
            ),
            (
                BELAYA_CHASHA_ID,
                "/static/uploads/works/work-04/02-detail.png",
                2,
            ),
            (
                BELAYA_CHASHA_ID,
                "/static/uploads/works/work-04/03-top.png",
                3,
            ),
            (
                BELAYA_CHASHA_ID,
                "/static/uploads/works/work-04/04-alt.png",
                4,
            ),
            (
                KRUZHKA_ID,
                "/static/uploads/works/work-05/01-cover.png",
                1,
            ),
            (
                KRUZHKA_ID,
                "/static/uploads/works/work-05/02-detail.png",
                2,
            ),
            (
                KRUZHKA_ID,
                "/static/uploads/works/work-05/03-alt.png",
                3,
            ),
        ]

        conn.executemany(
            """
            INSERT INTO work_images (
                work_id,
                image_path,
                position
            )
            VALUES (?, ?, ?)
            """,
            work_images,
        )

        category_ids = {
            row["slug"]: row["id"]
            for row in conn.execute("SELECT id, slug FROM categories").fetchall()
        }

        tag_ids = {
            row["slug"]: row["id"]
            for row in conn.execute("SELECT id, slug FROM tags").fetchall()
        }

        material_ids = {
            row["slug"]: row["id"]
            for row in conn.execute("SELECT id, slug FROM materials").fetchall()
        }

        work_categories = [
            (
                KAPLYA_ID,
                category_ids["objects"],
            ),
            (
                NIZKAYA_CHASHA_ID,
                category_ids["bowls"],
            ),
            (
                KOLONNA_ID,
                category_ids["objects"],
            ),
            (
                BELAYA_CHASHA_ID,
                category_ids["bowls"],
            ),
            (
                KRUZHKA_ID,
                category_ids["mugs"],
            ),
        ]

        conn.executemany(
            """
            INSERT INTO work_categories (
                work_id,
                category_id
            )
            VALUES (?, ?)
            """,
            work_categories,
        )

        work_tags = [
            (KAPLYA_ID, tag_ids["fragility"]),
            (KAPLYA_ID, tag_ids["nature"]),
            (NIZKAYA_CHASHA_ID, tag_ids["nature"]),
            (KOLONNA_ID, tag_ids["architecture"]),
            (KOLONNA_ID, tag_ids["fragility"]),
            (BELAYA_CHASHA_ID, tag_ids["fragility"]),
            (KRUZHKA_ID, tag_ids["home"]),
        ]

        conn.executemany(
            """
            INSERT INTO work_tags (
                work_id,
                tag_id
            )
            VALUES (?, ?)
            """,
            work_tags,
        )

        work_materials = [
            (KAPLYA_ID, material_ids["stoneware"]),
            (KAPLYA_ID, material_ids["glaze"]),
            (NIZKAYA_CHASHA_ID, material_ids["stoneware"]),
            (NIZKAYA_CHASHA_ID, material_ids["glaze"]),
            (KOLONNA_ID, material_ids["stoneware"]),
            (KOLONNA_ID, material_ids["porcelain"]),
            (KOLONNA_ID, material_ids["glaze"]),
            (BELAYA_CHASHA_ID, material_ids["porcelain"]),
            (BELAYA_CHASHA_ID, material_ids["glaze"]),
            (KRUZHKA_ID, material_ids["stoneware"]),
            (KRUZHKA_ID, material_ids["glaze"]),
        ]

        conn.executemany(
            """
            INSERT INTO work_materials (
                work_id,
                material_id
            )
            VALUES (?, ?)
            """,
            work_materials,
        )

        shop_items = [
            (
                "607e29e6-1aaf-4dd7-8719-934c89e61e01",
                KAPLYA_ID,
                None,
                None,
                None,
                None,
                30000,
                "unique",
                1,
                1,
                1,
                0,
            ),
            (
                "67beb49d-a621-47b0-903a-a101de072802",
                NIZKAYA_CHASHA_ID,
                None,
                None,
                None,
                None,
                18000,
                "unique",
                1,
                1,
                1,
                0,
            ),
            (
                "a2c59dc1-b349-47dd-8fb6-4318a43eaa03",
                KRUZHKA_ID,
                None,
                None,
                None,
                "Небольшая серия ручной работы.",
                6500,
                "stock",
                6,
                1,
                1,
                0,
            ),
        ]

        conn.executemany(
            """
            INSERT INTO shop_items (
                id,
                work_id,
                name,
                description,
                dimensions,
                sales_note,
                price,
                inventory_type,
                stock_quantity,
                is_published,
                is_orderable,
                is_retired
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            shop_items,
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def init_db():
    conn = get_db_connection()

    try:
        run_migrations(conn=conn, available_migrations=MIGRATIONS)
    finally:
        conn.close()

    seed_initial_data()
