def apply(conn):
    conn.execute(
        """
        CREATE TABLE orders (
            id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_phone TEXT,
            customer_address TEXT,
            items TEXT NOT NULL,
            total INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )