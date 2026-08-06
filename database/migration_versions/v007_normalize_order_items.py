import json


def create_order_items_table(conn):
    conn.execute(
        """
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            product_id TEXT,
            product_name TEXT NOT NULL,

            unit_price INTEGER NOT NULL
            CHECK (unit_price >= 0),

            quantity INTEGER NOT NULL
            CHECK (quantity > 0),

            FOREIGN KEY (order_id)
                REFERENCES orders(id)
                ON DELETE CASCADE,

            FOREIGN KEY (product_id)
                REFERENCES products(id)
                ON DELETE SET NULL
        )
        """
    )


def migrate_json_items(conn):
    existing_product_ids = {
        row["id"] for row in conn.execute("SELECT id FROM products").fetchall()
    }

    orders = conn.execute("SELECT id, items FROM orders ORDER BY id").fetchall()

    for order in orders:
        items = json.loads(order["items"])

        for product_id, item in items.items():
            linked_product_id = (
                product_id if product_id in existing_product_ids else None
            )

            conn.execute(
                """
                INSERT INTO order_items 
                    (order_id, product_id, product_name, unit_price, quantity)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    order["id"],
                    linked_product_id,
                    item["name"],
                    item["price"],
                    item["quantity"],
                ),
            )


def remove_json_items_column(conn):
    conn.execute("ALTER TABLE orders DROP COLUMN items")


def apply(conn):
    create_order_items_table(conn)
    migrate_json_items(conn)
    remove_json_items_column(conn)
