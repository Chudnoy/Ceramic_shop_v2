import sqlite3
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    apply: Callable[[sqlite3.Connection], None]


from database.migration_versions.v001_create_products import apply as apply_v001_create_products
from database.migration_versions.v002_add_categories import apply as apply_v002_create_categories


MIGRATIONS = (
    Migration(
        version=1,
        name='create_products',
        apply=apply_v001_create_products
    ),
    Migration(
        version=2,
        name='add_categories',
        apply=apply_v002_create_categories
    )
)


def ensure_schema_migrations_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def get_applied_migration_versions(conn):
    migration_data = conn.execute("SELECT version FROM schema_migrations").fetchall()

    return {migration['version'] for migration in migration_data}


def record_applied_migration(conn, version, name):
    conn.execute("INSERT INTO schema_migrations (version, name) VALUES (?, ?)", (version, name))


def get_pending_migrations(available_migrations, applied_versions):
    pending_migrations = []

    for migration in available_migrations:
        if migration.version not in applied_versions:
            pending_migrations.append(migration)

    return sorted(pending_migrations, key=lambda migration: migration.version)


def apply_migration(conn, migration):
    migration.apply(conn)

    record_applied_migration(
        conn=conn,
        version=migration.version,
        name=migration.name
    )


def run_migrations(conn, available_migrations):
    ensure_schema_migrations_table(conn)
    conn.commit()

    applied_versions = get_applied_migration_versions(conn)

    pending_migrations = get_pending_migrations(
        available_migrations,
        applied_versions
    )

    for migration in pending_migrations:
        try:
            conn.execute("BEGIN")
            apply_migration(conn, migration)
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def get_migration_by_version(available_migrations, version):
    for migration in available_migrations:
        if migration.version == version:
            return migration

    return None