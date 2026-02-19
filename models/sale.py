from database.db import get_db
from models.product import adjust_stock


def create_sale(items, notes, created_by, sale_date):
    total_amount = sum(i["selling_price"] * i["quantity"] for i in items)

    with get_db() as (conn, cursor):
        cursor.execute(
            "INSERT INTO sales (total_amount, sale_date, notes, created_by) VALUES (%s, %s, %s, %s)",
            (total_amount, sale_date, notes, created_by),
        )
        sale_id = cursor.lastrowid

        for item in items:
            adjust_stock(cursor, item["product_id"], -item["quantity"])
            cursor.execute(
                """
                INSERT INTO sale_items
                    (sale_id, product_id, quantity, selling_price, cost_price)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (sale_id, item["product_id"], item["quantity"],
                 item["selling_price"], item["cost_price"]),
            )

    return sale_id


def get_all(page=1, per_page=20, start_date=None, end_date=None):
    conditions = []
    params = []

    if start_date:
        conditions.append("s.sale_date >= %s")
        params.append(start_date)
    if end_date:
        conditions.append("s.sale_date <= %s")
        params.append(end_date)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    offset = (page - 1) * per_page

    with get_db() as (_, cursor):
        cursor.execute(
            f"""
            SELECT s.*, u.username AS created_by_name
            FROM sales s
            LEFT JOIN users u ON s.created_by = u.id
            {where}
            ORDER BY s.sale_date DESC, s.created_at DESC
            LIMIT %s OFFSET %s
            """,
            params + [per_page, offset],
        )
        sales = cursor.fetchall()
        cursor.execute(f"SELECT COUNT(*) AS total FROM sales s {where}", params)
        total = cursor.fetchone()["total"]

    return sales, total


def get_by_id(sale_id):
    with get_db() as (_, cursor):
        cursor.execute(
            """
            SELECT s.*, u.username AS created_by_name
            FROM sales s LEFT JOIN users u ON s.created_by = u.id
            WHERE s.id = %s
            """,
            (sale_id,),
        )
        sale = cursor.fetchone()
        if sale:
            cursor.execute(
                """
                SELECT si.*, p.name AS product_name
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                WHERE si.sale_id = %s
                """,
                (sale_id,),
            )
            sale["items"] = cursor.fetchall()
    return sale