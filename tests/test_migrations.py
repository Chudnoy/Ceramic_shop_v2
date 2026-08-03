import pytest
import sqlite3
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
        {
            "version": 3,
            "name": "add_work_images",
            "apply": fake_apply,
        },
        {
            "version": 1,
            "name": "initial_schema",
            "apply": fake_apply,
        },
        {
            "version": 2,
            "name": "add_projects",
            "apply": fake_apply,
        },
    ]

    applied_versions = {1, 3}

    pending_migrations = migrations.get_pending_migrations(available_migrations, applied_versions)

    assert [migration['version'] for migration in pending_migrations] == [2]


def test_get_pending_migrations_sorts_migrations_by_version():
    def fake_apply(conn):
        pass

    available_migrations = [
        {
            "version": 3,
            "name": "add_work_images",
            "apply": fake_apply,
        },
        {
            "version": 1,
            "name": "initial_schema",
            "apply": fake_apply,
        },
        {
            "version": 2,
            "name": "add_projects",
            "apply": fake_apply,
        },
    ]

    applied_versions = set()

    pending_migrations = migrations.get_pending_migrations(available_migrations, applied_versions)

    assert [migration['version'] for migration in pending_migrations] == [1, 2, 3]


def test_get_pending_migrations_returns_empty_list_when_all_applied():
    def fake_apply(conn):
        pass

    available_migrations = [
        {
            "version": 3,
            "name": "add_work_images",
            "apply": fake_apply,
        },
        {
            "version": 1,
            "name": "initial_schema",
            "apply": fake_apply,
        },
        {
            "version": 2,
            "name": "add_projects",
            "apply": fake_apply,
        },
    ]

    applied_versions = {1, 2, 3}

    pending_migrations = migrations.get_pending_migrations(available_migrations, applied_versions)
    
    assert pending_migrations == []


def test_apply_migration_applies_change_and_records_migration(db_connection):

    def create_test_table(conn):
        conn.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY)")

    migration = {
        'version': 1,
        'name': 'create_test_table',
        'apply': create_test_table
    }

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