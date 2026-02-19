from database.db import get_db


def get_all(page=1, per_page=20, search=None, category_id=None):
    offset = (page - 1) * per_page
    conditions = []
    params = []

    if search:
        conditions.append("(p.name LIKE %s OR p.barcode LIKE %s)")
        params += [f"%{search}%", f"%{search}%"]
    if category_id:
        conditions.append("p.category_id = %s")
        params.append(category_id)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with get_db() as (_, cursor):
        cursor.execute(
            f"""
            SELECT p.*, c.name AS category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            {where}
            ORDER BY p.name
            LIMIT %s OFFSET %s
            """,
            params + [per_page, offset],
        )
        products = cursor.fetchall()
        cursor.execute(f"SELECT COUNT(*) AS total FROM products p {where}", params)
        total = cursor.fetchone()["total"]

    return products, total


def get_by_id(product_id):
    with get_db() as (_, cursor):
        cursor.execute(
            """
            SELECT p.*, c.name AS category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s
            """,
            (product_id,),
        )
        return cursor.fetchone()


def get_by_barcode(barcode):
    with get_db() as (_, cursor):
        cursor.execute("SELECT * FROM products WHERE barcode = %s", (barcode,))
        return cursor.fetchone()


def create(data):
    with get_db() as (_, cursor):
        cursor.execute(
            """
            INSERT INTO products
                (name, category_id, cost_price, selling_price,
                 stock_quantity, minimum_stock_level, barcode)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["name"],
                data["category_id"],
                data["cost_price"],
                data["selling_price"],
                data.get("stock_quantity", 0),
                data.get("minimum_stock_level", 5),
                data.get("barcode"),
            ),
        )
        return cursor.lastrowid


def update(product_id, data):
    with get_db() as (_, cursor):
        cursor.execute(
            """
            UPDATE products SET
                name = %s, category_id = %s, cost_price = %s,
                selling_price = %s, minimum_stock_level = %s, barcode = %s
            WHERE id = %s
            """,
            (
                data["name"], data["category_id"], data["cost_price"],
                data["selling_price"], data.get("minimum_stock_level", 5),
                data.get("barcode"), product_id,
            ),
        )
        return cursor.rowcount


def delete(product_id):
    with get_db() as (_, cursor):
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        return cursor.rowcount


def get_low_stock():
    with get_db() as (_, cursor):
        cursor.execute(
            """
            SELECT p.*, c.name AS category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.stock_quantity <= p.minimum_stock_level
            ORDER BY (p.stock_quantity - p.minimum_stock_level) ASC
            """
        )
        return cursor.fetchall()


def adjust_stock(cursor, product_id, delta):
    cursor.execute(
        "SELECT stock_quantity FROM products WHERE id = %s FOR UPDATE",
        (product_id,),
    )
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"Product {product_id} not found.")
    new_qty = row["stock_quantity"] + delta
    if new_qty < 0:
        raise ValueError(
            f"Insufficient stock. Available: {row['stock_quantity']}, requested: {abs(delta)}"
        )
    cursor.execute(
        "UPDATE products SET stock_quantity = %s WHERE id = %s",
        (new_qty, product_id),
    )
    return new_qty