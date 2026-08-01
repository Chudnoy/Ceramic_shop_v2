from flask import Flask
import database.connection as connection


def test_get_db_connection_uses_database_from_app_config(tmp_path):
    app = Flask(__name__)
    
    database_path = tmp_path / "connection_test.db"
    app.config["DATABASE"] = str(database_path)
    
    with app.app_context():
        conn = connection.get_db_connection()
        
        conn.execute("""
            CREATE TABLE sample (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        conn.execute("INSERT INTO sample (name) VALUES (?)", ("Тестовая запись",))
        conn.commit()
        
        saved_row = conn.execute("SELECT name FROM sample").fetchone()
        foreign_keys_enabled = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        
        conn.close()
        
    assert database_path.exists()
    assert saved_row["name"] == "Тестовая запись"
    assert foreign_keys_enabled == 1