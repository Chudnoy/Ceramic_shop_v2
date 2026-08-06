def apply(conn):
    conn.execute(
        """
        CREATE TABLE tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE product_tags (
            product_id TEXT NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (product_id, tag_id),

            FOREIGN KEY (product_id)
                REFERENCES products(id)
                ON DELETE CASCADE,
            
            FOREIGN KEY (tag_id)
                REFERENCES tags(id)
                ON DELETE CASCADE
        )
        """
    )
