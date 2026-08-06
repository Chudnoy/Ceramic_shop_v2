def apply(conn):

    conn.execute(
        """
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            description TEXT
        )
        """
    )
    conn.execute(
        """
        ALTER TABLE products
        ADD COLUMN category_id INTEGER
        REFERENCES categories(id)
        """
    )
