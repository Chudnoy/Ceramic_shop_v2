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
from database.migration_versions.v003_create_orders_with_json_items import apply as apply_v003_create_orders_with_json_items
from database.migration_versions.v004_add_order_status import apply as apply_v004_add_order_status
from database.migration_versions.v005_expand_products import apply as apply_v005_expand_products
from database.migration_versions.v006_add_tags import apply as apply_v006_add_tags
from database.migration_versions.v007_normalize_order_items import apply as apply_v007_normalize_order_items


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
    ),
    Migration(
        version=3,
        name='create_orders_with_json_items',
        apply=apply_v003_create_orders_with_json_items
    ),
    Migration(
        version=4,
        name='add_order_status',
        apply=apply_v004_add_order_status
    ),
    Migration(
        version=5,
        name='expand_products',
        apply=apply_v005_expand_products
    ),
    Migration(
        version=6,
        name='add_tags',
        apply=apply_v006_add_tags
    ),
    Migration(
        version=7,
        name='normalize_order_items',
        apply=apply_v007_normalize_order_items
    )
)


def validate_migration_registry(available_migrations):

    versions = [migration.version for migration in available_migrations]
    names = [migration.name for migration in available_migrations]

    if any(type(version) is not int or version <= 0 for version in versions):
        raise ValueError('Версии миграций должны быть положительными целыми числами')

    if len(versions) != len(set(versions)):
        raise ValueError('Версии миграций не должны повторяться')

    if any(not isinstance(name, str) or not name.strip() for name in names):
        raise ValueError('Имя миграции должно быть непустой строкой')

    if len(names) != len(set(names)):
        raise ValueError('Имена миграций не должны повторяться')


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

    validate_migration_registry(available_migrations)

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