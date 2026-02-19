from database.db import get_db
from models.product import adjust_stock


def create_purchase(supplier_id, items, notes, created_by, purchase_date):
    total_amount = sum(i["cost_price"] * i["quantity"] for i in items)

    with get_db() as (conn, cursor):
        cursor.execute(
            """
            INSERT INTO purchases (supplier_id, total_amount, purchase_date, notes, created_by)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (supplier_id, total_amount, purchase_date, notes, created_by),
        )
        purchase_id = cursor.lastrowid

        for item in items:
            adjust_stock(cursor, item["product_id"], item["quantity"])
            cursor.execute(
                """
                INSERT INTO purchase_items (purchase_id, product_id, quantity, cost_price)
                VALUES (%s, %s, %s, %s)
                """,
                (purchase_id, item["product_id"], item["quantity"], item["cost_price"]),
            )

    return purchase_id


def get_all(page=1, per_page=20, start_date=None, end_date=None):
    conditions = []
    params = []

    if start_date:
        conditions.append("p.purchase_date >= %s")
        params.append(start_date)
    if end_date:
        conditions.append("p.purchase_date <= %s")
        params.append(end_date)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    offset = (page - 1) * per_page

    with get_db() as (_, cursor):
        cursor.execute(
            f"""
            SELECT p.*, s.name AS supplier_name, u.username AS created_by_name
            FROM purchases p
            JOIN suppliers s ON p.supplier_id = s.id
            LEFT JOIN users u ON p.created_by = u.id
            {where}
            ORDER BY p.purchase_date DESC, p.created_at DESC
            LIMIT %s OFFSET %s
            """,
            params + [per_page, offset],
        )
        purchases = cursor.fetchall()
        cursor.execute(f"SELECT COUNT(*) AS total FROM purchases p {where}", params)
        total = cursor.fetchone()["total"]

    return purchases, total


def get_by_id(purchase_id):
    with get_db() as (_, cursor):
        cursor.execute(
            """
            SELECT p.*, s.name AS supplier_name
            FROM purchases p JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.id = %s
            """,
            (purchase_id,),
        )
        purchase = cursor.fetchone()
        if purchase:
            cursor.execute(
                """
                SELECT pi.*, pr.name AS product_name
                FROM purchase_items pi
                JOIN products pr ON pi.product_id = pr.id
                WHERE pi.purchase_id = %s
                """,
                (purchase_id,),
            )
            purchase["items"] = cursor.fetchall()
    return purchase