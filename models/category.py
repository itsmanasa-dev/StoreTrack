from database.db import get_db


def get_all():
    with get_db() as (_, cursor):
        cursor.execute("SELECT * FROM categories ORDER BY name")
        return cursor.fetchall()


def create(name):
    with get_db() as (_, cursor):
        cursor.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
        return cursor.lastrowid


def delete(category_id):
    with get_db() as (_, cursor):
        cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
        return cursor.rowcount