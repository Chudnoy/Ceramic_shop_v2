import database.tags as tags

def replace_test_product_tags(conn, product_id, tag_ids):
    
    tags.replace_product_tags(
            conn=conn,
            product_id=product_id,
            tag_ids=tag_ids
    )
    
    
def test_update_tag_updates_fields(empty_db):
    
    tags.create_tag("Природа", "nature")
    
    old_tag = tags.get_tag_by_slug("nature")
    
    old_tag_id = old_tag["id"]
    
    tags.update_tag("Дом", "house", old_tag_id)
    
    new_tag = tags.get_tag_by_slug("house")
    
    new_tag_id = new_tag["id"]
    
    assert tags.get_tag_by_slug("nature") is None
    assert new_tag is not None
    assert new_tag_id == old_tag_id
    assert new_tag["name"] == "Дом"
    assert new_tag["slug"] == "house"
    
    
def test_add_tag_to_product_ensures_unique_product_tag_pair(empty_db, db_connection):
    tags.create_tag("Природа", "nature")
    
    conn = db_connection()
    conn.execute("INSERT INTO products (id, name, price) VALUES (?, ?, ?)", (1, "Белая ваза", 2000))
    conn.commit()
    conn.close()
    
    tags.add_tag_to_product(1, 1)
    tags.add_tag_to_product(1, 1)
    
    conn = db_connection()
    pairs_count = conn.execute("SELECT COUNT(*) FROM product_tags").fetchone()[0]
    conn.close()
    
    assert pairs_count == 1
    
    
def test_get_tags_for_product_returns_correct_sorted_tags(empty_db, db_connection):
    
    conn = db_connection()
    products = [
            (1, "Ваза", 1000),
            (2, "Чашка", 2000)
    ]
    conn.executemany("INSERT INTO products (id, name, price) VALUES (?, ?, ?)", products)
    conn.commit()
    conn.close()
    
    tags.create_tag("Природа", "nature")
    tags.create_tag("Дом", "house")
    tags.create_tag("Ветер", "wind")
    
    tags.add_tag_to_product(1, tags.get_tag_by_slug("nature")["id"])
    tags.add_tag_to_product(1, tags.get_tag_by_slug("house")["id"])
    tags.add_tag_to_product(2, tags.get_tag_by_slug("wind")["id"])
    
    conn = db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (1,)).fetchone()
    conn.close()
    
    tags_for_first_product = tags.get_tags_for_product(product["id"])
    
    tag_names = [tag["name"] for tag in tags_for_first_product]
    
    assert len(tag_names) == 2
    assert tag_names == ["Дом", "Природа"]
    
    
def test_update_product_tags_replaces_old_tags_with_new_tags(empty_db, db_connection):
    
    conn = db_connection()
    conn.execute("INSERT INTO products (id, name, price) VALUES (?, ?, ?)", (1, "Ваза", 1000))
    conn.commit()
    
    product = conn.execute("SELECT * FROM products WHERE id = ?", (1,)).fetchone()
    
    conn.close()
    
    tags.create_tag("Природа", "nature")
    tags.create_tag("Дом", "house")
    tags.create_tag("Ветер", "wind")
    
    tags.add_tag_to_product(1, tags.get_tag_by_slug("nature")["id"])
    tags.add_tag_to_product(1, tags.get_tag_by_slug("house")["id"])
    
    old_product_tags = [tag["name"] for tag in tags.get_tags_for_product(product["id"])]
    
    assert old_product_tags == ["Дом", "Природа"]

    conn = db_connection()
    replace_test_product_tags(conn, product["id"], [tags.get_tag_by_slug("wind")["id"], tags.get_tag_by_slug("house")["id"]])
    conn.commit()
    conn.close()
    
    new_product_tags = [tag["name"] for tag in tags.get_tags_for_product(product["id"])]
    
    assert "Природа" not in new_product_tags
    assert new_product_tags == ["Ветер", "Дом"]
    
    
def test_update_product_tags_deletes_tags_when_tags_list_is_empty(empty_db, db_connection):
    
    conn = db_connection()
    conn.execute("INSERT INTO products (id, name, price) VALUES (?, ?, ?)", (1, "Ваза", 1000))
    conn.commit()
    conn.close()
    
    tags.create_tag("Природа", "nature")
    tags.create_tag("Дом", "house")
    
    tags.add_tag_to_product(1, tags.get_tag_by_slug("nature")["id"])
    tags.add_tag_to_product(1, tags.get_tag_by_slug("house")["id"])
    
    old_product_tags = [tag["name"] for tag in tags.get_tags_for_product(1)]

    conn = db_connection()
    replace_test_product_tags(conn, 1, [])
    conn.commit()
    conn.close()
    
    new_product_tags = tags.get_tags_for_product(1)
    
    assert old_product_tags == ["Дом", "Природа"]
    assert new_product_tags == []
    
    
def test_get_tags_with_product_count_returns_correct_product_counts(empty_db, db_connection):
    
    conn = db_connection()
    products = [
            (1, "Ваза", 2000),
            (2, "Чашка", 3000)
    ]
    conn.executemany("INSERT INTO products (id, name, price) VALUES (?, ?, ?)", products)
    conn.commit()
    conn.close()
    
    tags.create_tag("Природа", "nature")
    tags.create_tag("Дом", "house")
    
    tags.add_tag_to_product(1, tags.get_tag_by_slug("nature")["id"])
    tags.add_tag_to_product(2, tags.get_tag_by_slug("nature")["id"])
    
    all_tags = tags.get_tags_with_product_count()
    
    counts_by_slug = {tag["slug"]: tag["products_count"] for tag in all_tags}
    
    assert len(all_tags) == 2
    assert counts_by_slug["nature"] == 2
    assert counts_by_slug["house"] == 0
    
    
def test_get_product_count_by_tag_id_returns_correct_product_counts(empty_db, db_connection):
    
    conn = db_connection()
    products = [
            (1, "Ваза", 1000),
            (2, "Чашка", 2000),
            (3, "Тарелка", 3000)
    ]
    conn.executemany("INSERT INTO products (id, name, price) VALUES (?, ?, ?)", products)
    conn.commit()
    conn.close()
    
    tags.create_tag("Природа", "nature")
    tags.create_tag("Дом", "house")
    
    nature_tag_id = tags.get_tag_by_slug("nature")["id"]
    house_tag_id = tags.get_tag_by_slug("house")["id"]
    
    tags.add_tag_to_product(1, nature_tag_id)
    tags.add_tag_to_product(2, nature_tag_id)
    tags.add_tag_to_product(3, house_tag_id)
    
    nature_tag_products_count = tags.get_product_count_by_tag_id(nature_tag_id)
    house_tag_products_count = tags.get_product_count_by_tag_id(house_tag_id)
    
    assert nature_tag_products_count == 2
    assert house_tag_products_count == 1
    assert tags.get_product_count_by_tag_id(444) == 0