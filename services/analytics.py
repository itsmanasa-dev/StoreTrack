import math
from database.db import get_db


def get_dashboard_stats():
    with get_db() as (_, cursor):
        cursor.execute("""
            SELECT COUNT(*) AS total_orders,
                   COALESCE(SUM(total_amount), 0) AS revenue
            FROM sales WHERE sale_date = CURDATE()
        """)
        today_sales = cursor.fetchone()

        cursor.execute("""
            SELECT COALESCE(SUM((si.selling_price - si.cost_price) * si.quantity), 0) AS profit
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            WHERE s.sale_date = CURDATE()
        """)
        today_profit = cursor.fetchone()["profit"]

        cursor.execute("""
            SELECT COUNT(*) AS total_products,
                   SUM(CASE WHEN stock_quantity <= minimum_stock_level THEN 1 ELSE 0 END) AS low_stock_count
            FROM products
        """)
        product_stats = cursor.fetchone()

        cursor.execute("""
            SELECT DATE_FORMAT(sale_date, '%Y-%m') AS month,
                   SUM(total_amount) AS revenue,
                   SUM((si.selling_price - si.cost_price) * si.quantity) AS profit
            FROM sales s
            JOIN sale_items si ON s.id = si.sale_id
            WHERE s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY month ORDER BY month ASC
        """)
        monthly_trend = cursor.fetchall()

        cursor.execute("""
            SELECT p.name, SUM(si.quantity) AS units_sold,
                   SUM(si.selling_price * si.quantity) AS revenue
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            GROUP BY si.product_id, p.name
            ORDER BY units_sold DESC LIMIT 5
        """)
        top_products = cursor.fetchall()

    return {
        "today_revenue": float(today_sales["revenue"]),
        "today_orders": today_sales["total_orders"],
        "today_profit": float(today_profit),
        "total_products": product_stats["total_products"],
        "low_stock_count": product_stats["low_stock_count"],
        "monthly_trend": [{**r, "revenue": float(r["revenue"]), "profit": float(r["profit"])} for r in monthly_trend],
        "top_products": [{**r, "revenue": float(r["revenue"])} for r in top_products],
    }


def get_profit_report(start_date, end_date, group_by="day"):
    fmt = "%Y-%m-%d" if group_by == "day" else "%Y-%m"
    with get_db() as (_, cursor):
        cursor.execute(f"""
            SELECT DATE_FORMAT(s.sale_date, %s) AS period,
                   SUM(si.selling_price * si.quantity) AS revenue,
                   SUM(si.cost_price * si.quantity) AS cost,
                   SUM((si.selling_price - si.cost_price) * si.quantity) AS profit,
                   COUNT(DISTINCT s.id) AS num_sales
            FROM sales s
            JOIN sale_items si ON s.id = si.sale_id
            WHERE s.sale_date BETWEEN %s AND %s
            GROUP BY period ORDER BY period ASC
        """, (fmt, start_date, end_date))
        rows = cursor.fetchall()
    return [{"period": r["period"], "revenue": float(r["revenue"]),
             "cost": float(r["cost"]), "profit": float(r["profit"]),
             "num_sales": r["num_sales"]} for r in rows]


def get_reorder_suggestions():
    with get_db() as (_, cursor):
        cursor.execute("""
            SELECT p.id, p.name, p.stock_quantity, p.minimum_stock_level,
                   COALESCE(SUM(si.quantity), 0) AS sold_last_30d,
                   COALESCE(SUM(si.quantity) / 30, 1) AS avg_daily_sales
            FROM products p
            LEFT JOIN sale_items si ON p.id = si.product_id
            LEFT JOIN sales s ON si.sale_id = s.id
                AND s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            WHERE p.stock_quantity <= p.minimum_stock_level
            GROUP BY p.id, p.name, p.stock_quantity, p.minimum_stock_level
            ORDER BY p.stock_quantity ASC
        """)
        rows = cursor.fetchall()

    suggestions = []
    for r in rows:
        reorder = max(
            math.ceil(r["avg_daily_sales"] * 30) - r["stock_quantity"],
            r["minimum_stock_level"] * 2,
        )
        suggestions.append({
            "id": r["id"], "name": r["name"],
            "stock_quantity": r["stock_quantity"],
            "minimum_stock_level": r["minimum_stock_level"],
            "sold_last_30d": r["sold_last_30d"],
            "avg_daily_sales": round(float(r["avg_daily_sales"]), 2),
            "suggested_reorder": reorder,
        })
    return suggestions