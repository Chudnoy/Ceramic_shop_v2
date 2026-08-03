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
        if migration['version'] not in applied_versions:
            pending_migrations.append(migration)

    return sorted(pending_migrations, key=lambda migration: migration['version'])


def apply_migration(conn, migration):
    migration['apply'](conn)

    record_applied_migration(
        conn=conn,
        version=migration['version'],
        name=migration['name']
    )