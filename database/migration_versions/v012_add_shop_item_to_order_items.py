def apply(conn):
    conn.execute(
        """
        ALTER TABLE order_items
        ADD COLUMN shop_item_id TEXT
            REFERENCES shop_items(id)
            ON DELETE SET NULL
        """
    )
