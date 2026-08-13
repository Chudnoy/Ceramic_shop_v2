def create_projects_table(conn):
    conn.execute(
        """
        CREATE TABLE projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            intro TEXT,
            text TEXT,
            period TEXT,
            is_published INTEGER NOT NULL DEFAULT 0
            CHECK (is_published IN (0, 1))
        )
        """
    )


def create_series_table(conn):
    conn.execute(
        """
        CREATE TABLE series (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
        """
    )


def create_materials_table(conn):
    conn.execute(
        """
        CREATE TABLE materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE
        )
        """
    )


def create_works_table(conn):
    conn.execute(
        """
        CREATE TABLE works (
            id TEXT PRIMARY KEY,
            slug TEXT UNIQUE,
            name TEXT NOT NULL,
            description TEXT,
            year INTEGER,
            dimensions TEXT,

            project_id TEXT,
            series_id TEXT,
            project_position INTEGER,

            is_published INTEGER NOT NULL DEFAULT 0
            CHECK (is_published IN (0, 1)),

            is_commissionable INTEGER NOT NULL DEFAULT 0
            CHECK (is_commissionable IN (0, 1)),

            commission_note TEXT,

            FOREIGN KEY (project_id)
                REFERENCES projects(id),

            FOREIGN KEY (series_id)
                REFERENCES series(id),

            CHECK (
                project_id IS NULL
                OR series_id IS NULL
            ),

            CHECK (
                project_position IS NULL
                OR project_position > 0
            ),

            CHECK (
                project_id IS NOT NULL
                OR project_position IS NULL
            ),

            UNIQUE (project_id, project_position)
        )
        """
    )


def create_project_images_table(conn):
    conn.execute(
        """
        CREATE TABLE project_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            image_path TEXT NOT NULL,

            position INTEGER NOT NULL
            CHECK (position > 0),

            UNIQUE (project_id, position),

            FOREIGN KEY (project_id)
                REFERENCES projects(id)
                ON DELETE CASCADE
        )
        """
    )


def create_work_images_table(conn):
    conn.execute(
        """
        CREATE TABLE work_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_id TEXT NOT NULL,
            image_path TEXT NOT NULL,

            position INTEGER NOT NULL
            CHECK (position > 0),

            UNIQUE (work_id, position),

            FOREIGN KEY (work_id)
                REFERENCES works(id)
                ON DELETE CASCADE
        )
        """
    )


def create_work_categories_table(conn):
    conn.execute(
        """
        CREATE TABLE work_categories (
            work_id TEXT NOT NULL,
            category_id INTEGER NOT NULL,

            PRIMARY KEY (work_id, category_id),

            FOREIGN KEY (work_id)
                REFERENCES works(id)
                ON DELETE CASCADE,

            FOREIGN KEY (category_id)
                REFERENCES categories(id)
        )
        """
    )


def create_work_tags_table(conn):
    conn.execute(
        """
        CREATE TABLE work_tags (
            work_id TEXT NOT NULL,
            tag_id INTEGER NOT NULL,

            PRIMARY KEY (work_id, tag_id),

            FOREIGN KEY (work_id)
                REFERENCES works(id)
                ON DELETE CASCADE,

            FOREIGN KEY (tag_id)
                REFERENCES tags(id)
                ON DELETE CASCADE
        )
        """
    )


def create_work_materials_table(conn):
    conn.execute(
        """
        CREATE TABLE work_materials (
            work_id TEXT NOT NULL,
            material_id INTEGER NOT NULL,

            PRIMARY KEY (work_id, material_id),

            FOREIGN KEY (work_id)
                REFERENCES works(id)
                ON DELETE CASCADE,

            FOREIGN KEY (material_id)
                REFERENCES materials(id)
        )
        """
    )


def apply(conn):
    create_projects_table(conn)
    create_series_table(conn)
    create_materials_table(conn)

    create_works_table(conn)

    create_project_images_table(conn)
    create_work_images_table(conn)

    create_work_categories_table(conn)
    create_work_tags_table(conn)
    create_work_materials_table(conn)
