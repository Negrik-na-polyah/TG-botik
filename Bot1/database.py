import sqlite3
from config import DB_NAME


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price INTEGER,
        category TEXT,
        photo TEXT
    )
    """)

    conn.commit()
    conn.close()


# 👇 ВОТ ЗДЕСЬ находится seed_products
def seed_products():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")

    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    cursor.execute("""
    INSERT INTO products (name, description, price, category, photo)
    VALUES (?, ?, ?, ?, ?)
    """, (
        "Мишка классический",
        "Очень мягкий плюшевый мишка",
        600,
        "bears",
        "AgACAgIAAxkBAAPlabF7cuIok6tj0FWrLzOl_DCRuFcAAm4ZaxtP0YhJwbNVaohqckwBAAMCAANtAAM6BA"
    ))

    conn.commit()
    conn.close()