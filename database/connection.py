import os
import sqlite3


DATABASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(DATABASE_DIR)
DB_PATH = os.path.join(PROJECT_DIR, "shop.db") 

def get_db_connection():
    """
Создаёт и возвращает подключение к SQLite-базе данных shop.db.

Настраивает row_factory на sqlite3.Row, чтобы строки результата можно было читать
как словари: row["name"], row["price"], row["status"]. Это упрощает работу с
данными в routes, services и шаблонах.
"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn