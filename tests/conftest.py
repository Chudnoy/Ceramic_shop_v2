import pytest
from werkzeug.security import generate_password_hash

import database.connection as connection
import database.migrations as migrations
from app import create_app

TEST_ADMIN_PASSWORD_HASH = generate_password_hash("test-password")


@pytest.fixture
def test_app(tmp_path):
    test_database_path = tmp_path / "test_shop.db"
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "ADMIN_LOGIN": "test-admin",
            "ADMIN_PASSWORD_HASH": TEST_ADMIN_PASSWORD_HASH,
            "DATABASE": str(test_database_path),
            "AUTO_INIT_DB": False,
        }
    )


@pytest.fixture
def client(test_app):
    return test_app.test_client()


@pytest.fixture
def app_context(test_app):
    with test_app.app_context():
        yield


@pytest.fixture
def db_connection(app_context):
    return connection.get_db_connection


@pytest.fixture
def empty_db(db_connection):
    conn = db_connection()

    try:
        migrations.run_migrations(conn=conn, available_migrations=migrations.MIGRATIONS)
    finally:
        conn.close()
