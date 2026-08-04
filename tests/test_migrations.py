import pytest
import sqlite3
from dataclasses import FrozenInstanceError
import database.migrations as migrations

def test_ensure_schema_migrations_table_creates_table(db_connection):

    conn = db_connection()
    migrations.ensure_schema_migrations_table(conn)
    conn.commit()
    saved_table = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?", ('schema_migrations',)).fetchall()
    conn.close()

    assert saved_table[0]['name'] == 'schema_migrations'


def test_ensure_schema_migrations_table_does_not_create_table_twice(db_connection):

    conn = db_connection()
    migrations.ensure_schema_migrations_table(conn)
    migrations.ensure_schema_migrations_table(conn)
    conn.commit()
    saved_table = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?", ('schema_migrations',)).fetchall()
    conn.close()

    assert len(saved_table) == 1


def test_get_applied_migration_versions_reads_migration_versions(db_connection):

    conn = db_connection()
    migrations.ensure_schema_migrations_table(conn)

    migrations_data = [
        (1, 'initial_schema'),
        (3, 'add_projects')
    ]

    conn.executemany("INSERT INTO schema_migrations (version, name) VALUES (?, ?)", migrations_data)
    conn.commit()
    migration_versions = migrations.get_applied_migration_versions(conn)
    conn.close()

    assert migration_versions is not None
    assert migration_versions == {1, 3}


def test_get_applied_migration_versions_returns_empty_set_when_no_migrations(db_connection):
    conn = db_connection()
    migrations.ensure_schema_migrations_table(conn)
    migration_versions = migrations.get_applied_migration_versions(conn)
    conn.close()

    assert migration_versions == set()


def test_record_applied_migration_saves_version_and_name(db_connection):

    conn = db_connection()
    migrations.ensure_schema_migrations_table(conn)
    migrations.record_applied_migration(conn, 1, 'add_projects')
    conn.commit()
    saved_migration = conn.execute("SELECT version, name FROM schema_migrations").fetchall()
    conn.close()

    assert len(saved_migration) == 1
    assert saved_migration[0]['version'] == 1
    assert saved_migration[0]['name'] == 'add_projects'


def test_record_applied_migration_rejects_repeated_record_with_same_version(db_connection):
    conn = db_connection()
    migrations.ensure_schema_migrations_table(conn)
    migrations.record_applied_migration(conn, 1, 'add_projects')
    conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        migrations.record_applied_migration(conn, 1, 'something')
    conn.rollback()

    saved_migration = conn.execute("SELECT version, name FROM schema_migrations").fetchall()
    conn.close()

    assert len(saved_migration) == 1
    assert saved_migration[0]['version'] == 1
    assert saved_migration[0]['name'] == 'add_projects'


def test_get_pending_migrations_excludes_applied_versions():

    def fake_apply(conn):
        pass

    available_migrations = [
        migrations.Migration(
            version = 3,
            name = "add_work_images",
            apply = fake_apply,
        ),
        migrations.Migration(
            version = 1,
            name = "initial_schema",
            apply = fake_apply,
        ),
        migrations.Migration(
            version = 2,
            name = "add_projects",
            apply = fake_apply,
        ),
    ]

    applied_versions = {1, 3}

    pending_migrations = migrations.get_pending_migrations(available_migrations, applied_versions)

    assert [migration.version for migration in pending_migrations] == [2]


def test_get_pending_migrations_sorts_migrations_by_version():
    def fake_apply(conn):
        pass

    available_migrations = [
        migrations.Migration(
            version = 3,
            name = "add_work_images",
            apply = fake_apply,
        ),
        migrations.Migration(
            version = 1,
            name = "initial_schema",
            apply = fake_apply,
        ),
        migrations.Migration(
            version = 2,
            name = "add_projects",
            apply = fake_apply,
        ),
    ]

    applied_versions = set()

    pending_migrations = migrations.get_pending_migrations(available_migrations, applied_versions)

    assert [migration.version for migration in pending_migrations] == [1, 2, 3]


def test_get_pending_migrations_returns_empty_list_when_all_applied():
    def fake_apply(conn):
        pass

    available_migrations = [
        migrations.Migration(
            version = 3,
            name = "add_work_images",
            apply = fake_apply,
        ),
        migrations.Migration(
            version = 1,
            name = "initial_schema",
            apply = fake_apply,
        ),
        migrations.Migration(
            version = 2,
            name = "add_projects",
            apply = fake_apply,
        ),
    ]

    applied_versions = {1, 2, 3}

    pending_migrations = migrations.get_pending_migrations(available_migrations, applied_versions)
    
    assert pending_migrations == []


def test_apply_migration_applies_change_and_records_migration(db_connection):

    def create_test_table(conn):
        conn.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY)")

    migration = migrations.Migration(
        version = 1,
        name = 'create_test_table',
        apply = create_test_table
    )

    conn = db_connection()
    migrations.ensure_schema_migrations_table(conn)
    migrations.apply_migration(conn, migration)
    conn.commit()

    saved_table = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?", ('test_table',)).fetchall()
    saved_migration = conn.execute("SELECT version, name FROM schema_migrations").fetchall()
    conn.close()

    assert len(saved_table) == 1

    assert len(saved_migration) == 1
    assert saved_migration[0]['version'] == 1
    assert saved_migration[0]['name'] == 'create_test_table'


def test_run_migrations_performs_correct_migrations(db_connection):

    def create_test_table(conn):
        conn.execute(
            """
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY
            )
            """
        )

    def add_name_column(conn):
        conn.execute(
            """
            ALTER TABLE test_table
            ADD COLUMN name TEXT
            """
        )

    available_migrations = [
        migrations.Migration(
            version = 2,
            name = "add_name_column",
            apply = add_name_column,
        ),
        migrations.Migration(
            version = 1,
            name = "create_test_table",
            apply = create_test_table,
        ),
    ]

    conn = db_connection()

    migrations.run_migrations(
        conn,
        available_migrations
    )

    saved_table = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        ("test_table",)
    ).fetchall()

    saved_migrations = conn.execute(
        """
        SELECT version, name
        FROM schema_migrations
        ORDER BY version
        """
    ).fetchall()

    columns = conn.execute(
        "PRAGMA table_info(test_table)"
    ).fetchall()

    column_names = [
        column["name"]
        for column in columns
    ]

    conn.close()

    assert len(saved_table) == 1
    assert "name" in column_names

    assert [row["version"] for row in saved_migrations] == [1, 2]

    assert [row["name"] for row in saved_migrations] == ["create_test_table", "add_name_column"]


def test_run_migrations_skips_already_applied_migrations(db_connection):

    def migration_that_should_not_run(conn):
        raise AssertionError('Миграция была запущена повторно')

    available_migrations = [
        migrations.Migration(
            version = 1,
            name = 'already_done',
            apply = migration_that_should_not_run
        )
    ]

    conn = db_connection()
    migrations.ensure_schema_migrations_table(conn)
    migrations.record_applied_migration(conn, 1, 'already_done')
    conn.commit()

    migrations.run_migrations(conn, available_migrations)

    saved_migrations = conn.execute("SELECT version, name FROM schema_migrations").fetchall()

    conn.close()

    assert len(saved_migrations) == 1
    assert saved_migrations[0]["version"] == 1
    assert saved_migrations[0]["name"] == "already_done"


def test_run_migrations_rolls_back_failed_migration(db_connection):

    def failing_migration(conn):
        conn.execute(
            """
            CREATE TABLE broken_table(
                id INTEGER PRIMARY KEY
            )
            """
        )
        raise RuntimeError('Ошибка миграции')

    available_migrations = [
        migrations.Migration(
            version = 1,
            name = 'broken_migration',
            apply = failing_migration
        )
    ]

    conn = db_connection()
    with pytest.raises(RuntimeError):
        migrations.run_migrations(conn, available_migrations)

    table = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name = ?
        """,
        ('broken_table',)
    ).fetchone()

    assert table is None

    saved_migrations = conn.execute(
        """
        SELECT *
        FROM schema_migrations
        """
    ).fetchall()

    assert saved_migrations == []

    schema_table = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name = ?
        """,
        ('schema_migrations',)
    ).fetchone()

    conn.close()

    assert schema_table is not None


def test_get_migration_by_version_returns_matching_migration():

    def fake_apply(conn):
        pass

    migration_1 = migrations.Migration(
        version=1,
        name="initial",
        apply=fake_apply,
    )

    migration_2 = migrations.Migration(
        version=2,
        name="orders",
        apply=fake_apply,
    )

    available_migrations = [
        migration_1,
        migration_2,
    ]

    found_migration = migrations.get_migration_by_version(available_migrations, 2)

    assert found_migration is migration_2


def test_get_migration_by_version_returns_none_when_version_not_found():

    def fake_apply(conn):
        pass

    available_migrations = [
        migrations.Migration(
            version=1,
            name="initial",
            apply=fake_apply,
        )
    ]

    found_migration = migrations.get_migration_by_version(available_migrations, 5)

    assert found_migration is None


def test_migration_stores_its_data():

    def fake_apply(conn):
        pass

    migration = migrations.Migration(
        version=1,
        name='initial_schema',
        apply=fake_apply
    )

    assert migration.version == 1
    assert migration.name == 'initial_schema'
    assert migration.apply is fake_apply


def test_migration_cannot_be_changed_after_creation():

    def fake_apply(conn):
        pass

    migration = migrations.Migration(
        version=1,
        name='initial_schema',
        apply=fake_apply
    )

    with pytest.raises(FrozenInstanceError):
        migration.version = 2


def test_validate_migration_registry_accepts_valid_migrations():
    def fake_apply(conn):
        pass

    available_migrations = (
        migrations.Migration(1, 'first', fake_apply),
        migrations.Migration(2, 'second', fake_apply)
    )

    migrations.validate_migration_registy(available_migrations)


def test_validate_migration_registry_rejects_duplicate_versions():
    def fake_apply(conn):
        pass

    available_migrations = (
        migrations.Migration(1, 'first', fake_apply),
        migrations.Migration(1, 'second', fake_apply)
    )

    with pytest.raises(
        ValueError,
        match='Версии миграций не должны повторяться'
    ):
        migrations.validate_migration_registy(available_migrations)


def test_validate_migration_registry_rejects_nonpositive_version():
    def fake_apply(conn):
        pass

    available_migrations = (
        migrations.Migration(0, 'invalid', fake_apply),
    )

    with pytest.raises(
        ValueError,
        match='Версии миграций должны быть положительными целыми числами'
    ):
        migrations.validate_migration_registy(available_migrations)