def apply(conn):
    conn.execute(
        """
        ALTER TABLE products
        ADD COLUMN status TEXT NOT NULL DEFAULT 'available'
        CHECK (
            status IN (
                'available',
                'reserved',
                'sold'
            )
        )
        """
    )

    conn.execute(
        """
        ALTER TABLE products
        ADD COLUMN year INTEGER
        """
    )

    conn.execute(
        """
        ALTER TABLE products
        ADD COLUMN materials TEXT NOT NULL
        DEFAULT 'Каменная масса'
        """
    )

    conn.execute(
        """
        ALTER TABLE products
        ADD COLUMN is_visible INTEGER NOT NULL DEFAULT 1
        CHECK (is_visible IN (0, 1))
        """
    )

    conn.execute(
        """
        ALTER TABLE products
        ADD COLUMN is_for_sale INTEGER NOT NULL DEFAULT 1
        CHECK (is_for_sale IN (0, 1))
        """
    )

    conn.execute(
        """
        ALTER TABLE products
        ADD COLUMN is_archived INTEGER NOT NULL DEFAULT 0
        CHECK (is_archived IN (0, 1))
        """
    )

    conn.execute(
        """
        ALTER TABLE products
        ADD COLUMN is_featured INTEGER NOT NULL DEFAULT 0
        CHECK (is_featured IN (0, 1))
        """
    )
