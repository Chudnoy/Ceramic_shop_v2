def apply(conn):
    conn.execute(
        """
        CREATE TABLE products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            img TEXT
        )
        """
    )