import pytest
import sqlite3
import database.products as products
import database.tags as tags
import database.reviews as reviews

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
        CREATE TABLE tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE
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
    
    conn.execute("""
        CREATE TABLE product_tags (
            product_id TEXT NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (product_id, tag_id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        )
    """)
    
    conn.execute("""
        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
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
    
    monkeypatch.setattr(
            tags,
            "get_db_connection",
            get_test_db_connection
    )
    
    monkeypatch.setattr(
            reviews,
            "get_db_connection",
            get_test_db_connection
    )
    
    return get_test_db_connection
    
    
def create_test_product(
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
            ):
    product_id = products.create_product(
            name=name,
            price=price,
            description=description,
            img_path=img_path,
            category_id=category_id,
            status=status,
            year=year,
            materials=materials,
            is_visible=is_visible,
            is_for_sale=is_for_sale,
            is_featured=is_featured
            )
            
    return product_id
    
    
def create_test_category(
                products_test_db,
                category_id=1,
                name="Вазы",
                slug="vases"
                ):
    conn = products_test_db()
    conn.execute("INSERT INTO categories (id, name, slug) VALUES (?, ?, ?)", (category_id, name, slug))
    conn.commit()
    conn.close()
    
    
def test_created_product_can_be_retrieved(products_test_db):
    
    create_test_category(products_test_db)
    product_id = create_test_product()
            
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
    
    create_test_category(products_test_db)
    product_id = create_test_product()
            
    products.update_product_state(product_id=product_id, status="sold", is_visible=0, is_for_sale=0, is_featured=1)
    
    product = products.get_product_by_id(product_id)
    
    assert product["status"] == "sold"
    assert product["is_visible"] == 0
    assert product["is_for_sale"] == 0
    assert product["is_featured"] == 1
    assert product["name"] == "Белая ваза"
    assert product["price"] == 9999
    
    
def test_set_product_archived_changes_only_archive_setting(products_test_db):
    
    create_test_category(products_test_db)
    product_id = create_test_product()
            
    assert products.get_product_by_id(product_id)["is_archived"] == 0
    products.set_product_archived(product_id, 1)
    assert products.get_product_by_id(product_id)["is_archived"] == 1
    products.set_product_archived(product_id, 0)
    
    product = products.get_product_by_id(product_id)
    assert product["is_archived"] == 0
    assert product["is_visible"] == 1
    assert product["is_for_sale"] == 1
    
    
def test_update_product_changes_all_product_data_except_id(products_test_db):
    
    create_test_category(products_test_db)
    product_id = create_test_product()
    
    create_test_category(
                    products_test_db,
                    category_id=2,
                    name="Чашки",
                    slug="cups"
                    )
    
    products.update_product(
                        product_id,
                        name="Чашка",
                        price=2500,
                        description="Синяя чашка",
                        img_path="Другой путь к картинке",
                        category_id=2,
                        status="reserved",
                        year=2022,
                        materials="Другие",
                        is_visible=0,
                        is_for_sale=0,
                        is_featured=1
                        )
                        
    product = products.get_product_by_id(product_id)
    
    assert product["id"] == product_id
    assert product["name"] == "Чашка"
    assert product["price"] == 2500
    assert product["description"] == "Синяя чашка"
    assert product["img"] == "Другой путь к картинке"
    assert product["category_id"] == 2
    assert product["status"] == "reserved"
    assert product["year"] == 2022
    assert product["materials"] == "Другие"
    assert product["is_visible"] == 0
    assert product["is_for_sale"] == 0
    assert product["is_featured"] == 1
    
    
def test_get_product_with_category_returns_correct_data(products_test_db):
    
    create_test_category(products_test_db)
    product_id = create_test_product()
    
    product = products.get_product_with_category(product_id)
    
    assert product is not None
    assert product["id"] == product_id
    assert product["name"] == "Белая ваза"
    assert product["price"] == 9999
    assert product["description"] == "Красивая белая ваза"
    assert product["img"] == "путь к картинке"
    assert product["category_id"] == 1
    assert product["status"] == "available"
    assert product["year"] == 2009
    assert product["materials"] == "ceramic"
    assert product["is_visible"] == 1
    assert product["is_for_sale"] == 1
    assert product["is_featured"] == 0
    assert product["category_name"] == "Вазы"
    assert product["category_slug"] == "vases"
    assert products.get_product_with_category(999) is None
    
    
def test_get_products_by_category_returns_products_only_in_its_category(products_test_db):
    create_test_category(products_test_db)
    create_test_category(
                products_test_db,
                category_id=2,
                name="Чашки",
                slug="cups"
                )
    create_test_product()
    create_test_product(
                name="Сны карелии",
                price=15000,
                description="Про природу",
                img_path="другой путь",
                category_id=1,
                year=2011
            )
    create_test_product(
            name="Детская чашка",
            price=3000,
            description="Розовая чашка",
            img_path="третий путь",
            category_id=2,
            year=2025,
            materials="Глина"
            )
            
    vases_products = products.get_products_by_category(1)
    
    vases_product_names = [product["name"] for product in vases_products]
    
    assert len(vases_products) == 2
    assert set(vases_product_names) == {"Белая ваза", "Сны карелии"}
    assert all(product["category_name"] == "Вазы" for product in vases_products)
    
    
def test_get_products_by_ids_returns_correct_products(products_test_db):
    create_test_category(products_test_db)
    white_vase_id = create_test_product()
    create_test_product(
                name="Сны карелии",
                price=15000,
                description="Про природу",
                img_path="другой путь",
                category_id=1,
                year=2011
            )
    kids_cup_id = create_test_product(
            name="Детская чашка",
            price=3000,
            description="Розовая чашка",
            img_path="третий путь",
            category_id=1,
            year=2025,
            materials="Глина"
            )
            
    two_products = products.get_products_by_ids([white_vase_id, kids_cup_id])
    two_products_names = {product["name"] for product in two_products}
    
    assert two_products_names == {"Белая ваза", "Детская чашка"}
    
    
def test_get_products_by_ids_returns_empty_list_without_db_call(monkeypatch):
    
    def fail_if_called():
        raise AssertionError("Подключение к базе не должно вызываться")
        
    monkeypatch.setattr(
            products,
            "get_db_connection",
            fail_if_called
    )
    
    result = products.get_products_by_ids([])
    
    assert result == []
    
    
def test_get_all_products_returns_only_visible_non_archived_products(products_test_db):
    
    create_test_category(products_test_db)
    
    create_test_product()
    
    create_test_product(
                name="Сны карелии",
                price=15000,
                description="Про природу",
                img_path="другой путь",
                category_id=1,
                year=2011,
                is_visible=0
            )
    third_id = create_test_product(
            name="Детская чашка",
            price=3000,
            description="Розовая чашка",
            img_path="третий путь",
            category_id=1,
            year=2025,
            materials="Глина"
            )
            
    products.set_product_archived(third_id, 1)
    
    all_products = products.get_all_products()
    
    product_names = {product["name"] for product in all_products}
    
    assert len(all_products) == 1
    assert product_names == {"Белая ваза"}
    
    
def test_get_all_products_returns_non_archived_products(products_test_db):
    
    create_test_category(products_test_db)
    
    create_test_product()
    
    create_test_product(
                name="Сны карелии",
                price=15000,
                description="Про природу",
                img_path="другой путь",
                category_id=1,
                year=2011,
                is_visible=0
            )
    third_id = create_test_product(
            name="Детская чашка",
            price=3000,
            description="Розовая чашка",
            img_path="третий путь",
            category_id=1,
            year=2025,
            materials="Глина",
            is_visible=1
            )
            
    products.set_product_archived(third_id, 1)
    
    all_products = products.get_all_products(only_visible=False)
    
    product_names = {product["name"] for product in all_products}
    
    assert len(all_products) == 2
    assert product_names == {"Сны карелии", "Белая ваза"}
    
    
def test_get_all_products_returns_only_archived_products(products_test_db):
    create_test_category(products_test_db)
    
    first_id = create_test_product()
    
    create_test_product(
                name="Сны карелии",
                price=15000,
                description="Про природу",
                img_path="другой путь",
                category_id=1,
                year=2011,
                is_visible=1
            )
    third_id = create_test_product(
            name="Детская чашка",
            price=3000,
            description="Розовая чашка",
            img_path="третий путь",
            category_id=1,
            year=2025,
            materials="Глина",
            is_visible=0
            )
            
    products.set_product_archived(first_id, 1)
    products.set_product_archived(third_id, 1)
    
    all_products = products.get_all_products(only_visible=False, is_archived=True)
    
    product_names = {product["name"] for product in all_products}
    
    assert len(all_products) == 2
    assert product_names == {"Детская чашка", "Белая ваза"}
    
    
def test_get_all_products_returns_only_featured_products(products_test_db):
    
    create_test_category(products_test_db)
    
    create_test_product(is_featured=1)
    
    create_test_product(
                name="Сны карелии",
                price=15000,
                description="Про природу",
                img_path="другой путь",
                category_id=1,
                year=2011,
            )
    create_test_product(
            name="Детская чашка",
            price=3000,
            description="Розовая чашка",
            img_path="третий путь",
            category_id=1,
            year=2025,
            materials="Глина",
            is_featured=1
            )
            
    all_products = products.get_all_products(only_featured=True)
    
    product_names = {product["name"] for product in all_products}
    
    assert len(all_products) == 2
    assert product_names == {"Белая ваза", "Детская чашка"}
    
    
def test_get_all_products_returns_only_featured_and_visible_products(products_test_db):
    create_test_category(products_test_db)
    
    create_test_product()
    
    create_test_product(
                name="Сны карелии",
                price=15000,
                description="Про природу",
                img_path="другой путь",
                category_id=1,
                year=2011,
                is_visible=0,
                is_featured=1
            )
    create_test_product(
            name="Детская чашка",
            price=3000,
            description="Розовая чашка",
            img_path="третий путь",
            category_id=1,
            year=2025,
            materials="Глина",
            is_visible=1,
            is_featured=1
            )
    
    all_products = products.get_all_products(only_visible=True, only_featured=True)
    
    product_names = {product["name"] for product in all_products}
    
    assert product_names == {"Детская чашка"}
    
    
def test_get_all_products_filters_by_normalized_status(products_test_db):
    create_test_category(products_test_db)
    
    create_test_product(status="sold")
    
    create_test_product(
                name="Сны карелии",
                price=15000,
                description="Про природу",
                img_path="другой путь",
                category_id=1,
                year=2011,
                status="available"
            )
    create_test_product(
            name="Детская чашка",
            price=3000,
            description="Розовая чашка",
            img_path="третий путь",
            category_id=1,
            year=2025,
            materials="Глина",
            status="reserved"
            )
            
    
    all_products = products.get_all_products(status="  SOLD ")
    
    product_names = {product["name"] for product in all_products}
    
    assert product_names == {"Белая ваза"}
    
    
def test_get_all_products_ignores_invalid_status(products_test_db):
    create_test_category(products_test_db)
    create_test_product()
    create_test_product(name="Чашка", status="reserved")
    create_test_product(name="Тарелка", status="sold")
    
    all_products = products.get_all_products(status="aaa")
    
    product_names = {product["name"] for product in all_products}
    
    assert product_names == {"Белая ваза", "Чашка", "Тарелка"}
    
    
def test_get_all_products_filters_by_category_slug(products_test_db):
    create_test_category(products_test_db)
    create_test_category(
            products_test_db,
            category_id=2,
            name="Чашки",
            slug="cups"
    )
    
    create_test_product()
    create_test_product(
            name="Сны Карелии",
            category_id=1
    )
    create_test_product(
            name="Кружка",
            category_id=2
    )
    
    all_products = products.get_all_products(category_slug="vases")
    
    product_names = {product["name"] for product in all_products}
    
    assert product_names == {"Белая ваза", "Сны Карелии"}
    
    
def test_get_all_products_searches_by_name_and_description(products_test_db):
    create_test_category(products_test_db)
    create_test_product(
            name="Белая ваза",
            description="Керамический объект"
            )
    create_test_product(
            name="Сны Карелии",
            description="ваза по природным мотивам"
            )
    create_test_product(
            name="Кружка",
            description="Детская кружка"
    )
    
    all_products = products.get_all_products(search_query="ваза")
    
    product_names = {product["name"] for product in all_products}
    
    assert product_names == {"Белая ваза", "Сны Карелии"}
    
    
def test_get_all_products_sorts_by_price(products_test_db):
    create_test_category(products_test_db)
    create_test_product(price=5000)
    create_test_product(
            name="Сны Карелии",
            description="На природные мотивы",
            price=10000
    )
    create_test_product(
            name="Детская кружка",
            description="Розовая кружка",
            price=2500
    )
    
    all_products = products.get_all_products(sort_by="price", order="ASC")
    
    product_names = [product["name"] for product in all_products]
    
    assert product_names == ["Детская кружка", "Белая ваза", "Сны Карелии"]
    
    all_products = products.get_all_products(sort_by="price", order="DESC")
    
    product_names = [product["name"] for product in all_products]
    
    assert product_names == ["Сны Карелии", "Белая ваза", "Детская кружка"]
    
    
def test_get_all_products_ignores_invalid_sort_data(products_test_db):
    
    create_test_category(products_test_db)
    create_test_product(price=5000)
    create_test_product(
            name="Сны Карелии",
            description="На природные мотивы",
            price=10000
    )
    create_test_product(
            name="Детская кружка",
            description="Розовая кружка",
            price=2500
    )
    
    all_products = products.get_all_products(sort_by="banana", order="sideways")
    
    product_names = [product["name"] for product in all_products]
    
    assert product_names == ["Белая ваза", "Детская кружка", "Сны Карелии"]
    
    
def test_delete_product_completely_removes_product_dependencies(products_test_db):
    
    create_test_category(products_test_db)
    tags.create_tag("Природа", "nature")
    product_id = create_test_product()
    tag_id = tags.get_tag_by_slug("nature")["id"]
    tags.add_tag_to_product(product_id, tag_id)
    reviews.add_review_db(
            product_id=product_id,
            name="Денис",
            rating=4,
            comment="Нормально"
            )
    products.delete_product(product_id)
    
    product = products.get_product_by_id(product_id)
    
    assert product is None
    
    conn = products_test_db()

    product_tags_count = conn.execute("SELECT COUNT(*) FROM product_tags WHERE product_id = ?", (product_id,)).fetchone()[0]
    
    reviews_count = conn.execute("SELECT COUNT(*) FROM reviews WHERE product_id = ?",(product_id,)).fetchone()[0]
    
    conn.close()
    
    assert product_tags_count == 0
    assert reviews_count == 0