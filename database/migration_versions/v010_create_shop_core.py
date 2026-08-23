def create_shop_items_table(conn):
    conn.execute(
        """
        CREATE TABLE shop_items (
            id TEXT PRIMARY KEY,

            work_id TEXT UNIQUE,

            name TEXT,
            description TEXT,
            dimensions TEXT,
            sales_note TEXT,

            price INTEGER NOT NULL
            CHECK (price >= 0),

            inventory_type TEXT NOT NULL
            CHECK (
                inventory_type IN ('unique', 'stock')
            ),

            stock_quantity INTEGER NOT NULL
            CHECK (stock_quantity >= 0),

            is_published INTEGER NOT NULL DEFAULT 0
            CHECK (is_published IN (0, 1)),

            is_orderable INTEGER NOT NULL DEFAULT 0
            CHECK (is_orderable IN (0, 1)),

            is_retired INTEGER NOT NULL DEFAULT 0
            CHECK (is_retired IN (0, 1)),

            FOREIGN KEY (work_id)
                REFERENCES works(id),

            CHECK (
                work_id IS NOT NULL
                OR (
                    name IS NOT NULL
                    AND TRIM(name) != ''
                )
            ),

            CHECK (
                work_id IS NULL
                OR name IS NULL
            ),

            CHECK (
                work_id IS NULL
                OR description IS NULL
            ),

            CHECK (
                work_id IS NULL
                OR dimensions IS NULL
            ),

            CHECK (
                inventory_type != 'unique'
                OR stock_quantity IN (0, 1)
            )
        )
        """
    )


def create_shop_item_images_table(conn):
    conn.execute(
        """
        CREATE TABLE shop_item_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_item_id TEXT NOT NULL,
            image_path TEXT NOT NULL,
            position INTEGER NOT NULL
            CHECK (position > 0),
            UNIQUE (shop_item_id, position),
            FOREIGN KEY (shop_item_id)
                REFERENCES shop_items(id)
                ON DELETE CASCADE
        )
        """
    )


def create_shop_item_categories_table(conn):
    conn.execute(
        """
        CREATE TABLE shop_item_categories (
            shop_item_id TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            PRIMARY KEY (shop_item_id, category_id),

            FOREIGN KEY (shop_item_id)
                REFERENCES shop_items(id)
                ON DELETE CASCADE,
            
            FOREIGN KEY (category_id)
                REFERENCES categories(id)
        )
        """
    )


def create_shop_item_tags_table(conn):
    conn.execute(
        """
        CREATE TABLE shop_item_tags (
            shop_item_id TEXT NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (shop_item_id, tag_id),

            FOREIGN KEY (shop_item_id)
                REFERENCES shop_items(id)
                ON DELETE CASCADE,

            FOREIGN KEY (tag_id)
                REFERENCES tags(id)
                ON DELETE CASCADE
        )
        """
    )


def create_shop_item_materials_table(conn):
    conn.execute(
        """
        CREATE TABLE shop_item_materials (
            shop_item_id TEXT NOT NULL,
            material_id INTEGER NOT NULL,
            PRIMARY KEY (shop_item_id, material_id),

            FOREIGN KEY (shop_item_id)
                REFERENCES shop_items(id)
                ON DELETE CASCADE,

            FOREIGN KEY (material_id)
                REFERENCES materials(id)
        )
        """
    )


def apply(conn):
    create_shop_items_table(conn)
    create_shop_item_images_table(conn)
    create_shop_item_categories_table(conn)
    create_shop_item_tags_table(conn)
    create_shop_item_materials_table(conn)
