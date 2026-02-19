from database.db import get_db


def get_all():
    with get_db() as (_, cursor):
        cursor.execute("SELECT * FROM suppliers ORDER BY name")
        return cursor.fetchall()


def get_by_id(supplier_id):
    with get_db() as (_, cursor):
        cursor.execute("SELECT * FROM suppliers WHERE id = %s", (supplier_id,))
        return cursor.fetchone()


def create(data):
    with get_db() as (_, cursor):
        cursor.execute(
            "INSERT INTO suppliers (name, phone, email, address) VALUES (%s, %s, %s, %s)",
            (data["name"], data.get("phone"), data.get("email"), data.get("address")),
        )
        return cursor.lastrowid


def update(supplier_id, data):
    with get_db() as (_, cursor):
        cursor.execute(
            "UPDATE suppliers SET name=%s, phone=%s, email=%s, address=%s WHERE id=%s",
            (data["name"], data.get("phone"), data.get("email"), data.get("address"), supplier_id),
        )
        return cursor.rowcount


def delete(supplier_id):
    with get_db() as (_, cursor):
        cursor.execute("DELETE FROM suppliers WHERE id = %s", (supplier_id,))
        return cursor.rowcount