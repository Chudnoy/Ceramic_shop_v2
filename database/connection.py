import sqlite3

def get_db_connection():
    """
Создаёт и возвращает подключение к SQLite-базе данных shop.db.

Настраивает row_factory на sqlite3.Row, чтобы строки результата можно было читать
как словари: row["name"], row["price"], row["status"]. Это упрощает работу с
данными в routes, services и шаблонах.
"""
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    return conn