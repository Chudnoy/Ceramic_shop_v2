def apply(conn):
    conn.execute(
        """
        ALTER TABLE orders
        ADD COLUMN status text NOT NULL DEFAULT 'new'
        CHECK (
            status in (
                'new',
                'confirmed',
                'completed',
                'canceled'
            )
        )
        """
    )