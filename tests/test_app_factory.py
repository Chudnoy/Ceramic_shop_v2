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


def test_create_app_does_not_initialize_database(tmp_path):
    database_path = tmp_path / "factory-test.db"

    create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "ADMIN_LOGIN": "test-admin",
            "ADMIN_PASSWORD_HASH": "test-password-hash",
            "DATABASE": str(database_path),
        }
    )

    assert database_path.exists() is False
