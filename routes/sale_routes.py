from flask import Blueprint, request, jsonify, session
from models import sale as sale_model
from models.product import get_by_id as get_product
from services.auth import login_required
from services.export import export_csv
from datetime import date

sale_bp = Blueprint("sales", __name__, url_prefix="/api/sales")


@sale_bp.route("/", methods=["GET"])
@login_required
def list_sales():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    sales, total = sale_model.get_all(page, per_page, start_date, end_date)
    return jsonify({"sales": sales, "total": total, "page": page, "pages": -(-total // per_page)})


@sale_bp.route("/<int:sale_id>", methods=["GET"])
@login_required
def get_sale(sale_id):
    s = sale_model.get_by_id(sale_id)
    if not s:
        return jsonify({"error": "Sale not found"}), 404
    return jsonify(s)


@sale_bp.route("/", methods=["POST"])
@login_required
def create_sale():
    data = request.get_json()
    items = data.get("items", [])
    if not items:
        return jsonify({"error": "At least one item is required"}), 400

    enriched_items = []
    for item in items:
        product = get_product(item.get("product_id"))
        if not product:
            return jsonify({"error": f"Product {item.get('product_id')} not found"}), 404
        qty = int(item.get("quantity", 0))
        if qty <= 0:
            return jsonify({"error": "Quantity must be > 0"}), 400
        enriched_items.append({
            "product_id": product["id"],
            "quantity": qty,
            "selling_price": float(item.get("selling_price", product["selling_price"])),
            "cost_price": float(product["cost_price"]),
        })

    sale_date = data.get("sale_date", str(date.today()))
    notes = data.get("notes", "")
    created_by = session.get("user_id")

    try:
        sale_id = sale_model.create_sale(enriched_items, notes, created_by, sale_date)
        return jsonify({"id": sale_id, "message": "Sale recorded"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@sale_bp.route("/export", methods=["GET"])
@login_required
def export():
    sales, _ = sale_model.get_all(page=1, per_page=10000,
                                   start_date=request.args.get("start_date"),
                                   end_date=request.args.get("end_date"))
    headers = ["id", "total_amount", "sale_date", "created_by_name", "notes"]
    return export_csv(headers, sales, "sales.csv")