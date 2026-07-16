import pytest
import sqlite3
import database.products as products

@pytest.fixture
def products_test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_shop.db"
    
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            description TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'available',
            img TEXT,
            category_id INTEGER,
            year INTEGER,
            materials TEXT NOT NULL DEFAULT 'Каменная масса',
            is_visible INTEGER NOT NULL DEFAULT 1,
            is_for_sale INTEGER NOT NULL DEFAULT 1,
            is_archived INTEGER NOT NULL DEFAULT 0,
            is_featured INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)
    conn.commit()
    conn.close()
    
    def get_test_db_connection():
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn
        
    monkeypatch.setattr(
            products,
            "get_db_connection",
            get_test_db_connection
    )
    
    return get_test_db_connection
    
    
def create_test_category_and_product(products_test_db):
    conn = products_test_db()
    conn.execute("INSERT INTO categories (id, name, slug) VALUES (?, ?, ?)", (1, "Вазы", "vases"))
    conn.commit()
    conn.close()
    
    product_id = products.create_product(
            name="Белая ваза",
            price=9999,
            description="Красивая белая ваза",
            img_path="путь к картинке",
            category_id=1,
            status="available",
            year=2009,
            materials="ceramic",
            is_visible=1,
            is_for_sale=1,
            is_featured=0
            )
            
    return product_id
    
    
def test_product_creation_and_verify_retrieval_and_existence(products_test_db):
    
    product_id = create_test_category_and_product(products_test_db)
            
    product = products.get_product_by_id(product_id)
    
    
    assert product is not None
    assert isinstance(product["id"], str)
    assert product["id"] == product_id
    assert product["name"] == "Белая ваза"
    assert product["price"] == 9999
    assert products.product_exists(product_id) is True
    assert products.product_exists("999") is False
    assert product["status"] == "available"
    assert product["is_visible"] == 1
    assert product["category_id"] == 1
    
    
def test_update_product_state_changes_only_product_state(products_test_db):
    
    product_id = create_test_category_and_product(products_test_db)
            
    products.update_product_state(product_id=product_id, status="sold", is_visible=0, is_for_sale=0, is_featured=1)
    
    product = products.get_product_by_id(product_id)
    
    assert product["status"] == "sold"
    assert product["is_visible"] == 0
    assert product["is_for_sale"] == 0
    assert product["is_featured"] == 1
    assert product["name"] == "Белая ваза"
    assert product["price"] == 9999
    
    
def test_set_product_archived_changes_only_archive_setting(products_test_db):
    
    product_id = create_test_category_and_product(products_test_db)
            
    assert products.get_product_by_id(product_id)["is_archived"] == 0
    products.set_product_archived(product_id, 1)
    assert products.get_product_by_id(product_id)["is_archived"] == 1
    products.set_product_archived(product_id, 0)
    
    product = products.get_product_by_id(product_id)
    assert product["is_archived"] == 0
    assert product["is_visible"] == 1
    assert product["is_for_sale"] == 1