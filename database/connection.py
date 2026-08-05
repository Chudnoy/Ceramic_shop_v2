import sqlite3

from flask import current_app


def get_db_connection():
    """
Создаёт и возвращает подключение к SQLite-базе данных shop.db.

Настраивает row_factory на sqlite3.Row, чтобы строки результата можно было читать
как словари: row["name"], row["price"], row["status"]. Это упрощает работу с
данными в routes, services и шаблонах.
"""
    database_path = current_app.config["DATABASE"]
    conn = sqlite3.connect(database_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn