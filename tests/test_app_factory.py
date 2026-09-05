import sqlite3

import pytest

from app import create_app


def test_create_app_applies_test_config(tmp_path):
    database_path = tmp_path / "factory-test.db"

    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "factory-secret",
            "ADMIN_LOGIN": "factory-admin",
            "ADMIN_PASSWORD_HASH": "factory-password-hash",
            "DATABASE": str(database_path),
        }
    )

    assert app.testing is True
    assert app.config["SECRET_KEY"] == "factory-secret"
    assert app.config["ADMIN_LOGIN"] == "factory-admin"
    assert app.config["ADMIN_PASSWORD_HASH"] == "factory-password-hash"
    assert app.config["DATABASE"] == str(database_path)


@pytest.mark.parametrize(
    ("missing_key", "expected_message"),
    [
        ("SECRET_KEY", "SECRET_KEY не задан"),
        ("ADMIN_LOGIN", "ADMIN_LOGIN не задан"),
        (
            "ADMIN_PASSWORD_HASH",
            "ADMIN_PASSWORD_HASH не задан",
        ),
    ],
)
def test_create_app_rejects_missing_required_config(
    tmp_path,
    missing_key,
    expected_message,
):
    config = {
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "ADMIN_LOGIN": "test-admin",
        "ADMIN_PASSWORD_HASH": "test-password-hash",
        "DATABASE": str(tmp_path / "test.db"),
    }

    config[missing_key] = None

    with pytest.raises(RuntimeError, match=expected_message):
        create_app(config)


def test_create_app_initializes_database_and_seeds_initial_data(tmp_path):
    database_path = tmp_path / "factory-test.db"

    config = {
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "ADMIN_LOGIN": "test-admin",
        "ADMIN_PASSWORD_HASH": "test-password-hash",
        "DATABASE": str(database_path),
    }

    create_app(config)
    create_app(config)

    assert database_path.exists() is True

    conn = sqlite3.connect(database_path)

    try:
        table_names = {
            row[0]
            for row in conn.execute(
                """
                SELECT name
                FROM sqlite_schema
                WHERE type = 'table'
                """
            ).fetchall()
        }

        migration_versions = [
            row[0]
            for row in conn.execute(
                """
                SELECT version
                FROM schema_migrations
                ORDER BY version
                """
            ).fetchall()
        ]

        category_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        tag_count = conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
        product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        work_count = conn.execute("SELECT COUNT(*) FROM works").fetchone()[0]
        shop_item_count = conn.execute("SELECT COUNT(*) FROM shop_items").fetchone()[0]
        work_image_count = conn.execute("SELECT COUNT(*) FROM work_images").fetchone()[
            0
        ]
    finally:
        conn.close()

    expected_tables = {
        "schema_migrations",
        "products",
        "categories",
        "orders",
        "tags",
        "product_tags",
        "order_items",
    }

    assert expected_tables <= table_names

    assert migration_versions == [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
    ]

    assert category_count == 5
    assert tag_count == 6

    assert product_count == 0
    assert work_count == 5
    assert shop_item_count == 3
    assert work_image_count == 19


def test_create_app_skips_database_initialization_when_disabled(tmp_path):
    database_path = tmp_path / "factory-test.db"

    create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "ADMIN_LOGIN": "test-admin",
            "ADMIN_PASSWORD_HASH": "test-password-hash",
            "DATABASE": str(database_path),
            "AUTO_INIT_DB": False,
        }
    )

    assert database_path.exists() is False
