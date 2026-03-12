import sqlite3
from config import DB_NAME


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    """Create required tables if they do not exist."""

    with get_connection() as conn:
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

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price INTEGER,
            name TEXT,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)


def seed_products():
    """Seed the database with a few products if it is empty."""

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] > 0:
            return

        products = [
            (
                "Мишка классический",
                "Очень мягкий плюшевый мишка, идеальный подарок для детей и взрослых",
                600,
                "bears",
                "AgACAgIAAxkBAAPlabF7cuIok6tj0FWrLzOl_DCRuFcAAm4ZaxtP0YhJwbNVaohqckwBAAMCAANtAAM6BA"
            ),
            (
                "Мишка Тедди",
                "Классический медведь Тедди с бантиком, высота 30 см",
                850,
                "bears",
                "AgACAgIAAxkBAAPlabF7cuIok6tj0FWrLzOl_DCRuFcAAm4ZaxtP0YhJwbNVaohqckwBAAMCAANtAAM6BA"
            ),
            (
                "Уточка стандарт",
                "Жёлтая резиновая уточка — классика жанра",
                300,
                "ducks",
                "AgACAgIAAxkBAAPlabF7cuIok6tj0FWrLzOl_DCRuFcAAm4ZaxtP0YhJwbNVaohqckwBAAMCAANtAAM6BA"
            ),
            (
                "Овен ♈",
                "Мягкая игрушка знака зодиака Овен",
                750,
                "zodiac",
                "AgACAgIAAxkBAAPlabF7cuIok6tj0FWrLzOl_DCRuFcAAm4ZaxtP0YhJwbNVaohqckwBAAMCAANtAAM6BA"
            ),
        ]

        cursor.executemany("""
        INSERT INTO products (name, description, price, category, photo)
        VALUES (?, ?, ?, ?, ?)
        """, products)
