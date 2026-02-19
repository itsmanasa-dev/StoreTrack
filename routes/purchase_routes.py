from flask import Blueprint, request, jsonify, session
from models import purchase as purchase_model
from services.auth import login_required
from services.export import export_csv
from datetime import date

purchase_bp = Blueprint("purchases", __name__, url_prefix="/api/purchases")


@purchase_bp.route("/", methods=["GET"])
@login_required
def list_purchases():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    purchases, total = purchase_model.get_all(page, per_page, start_date, end_date)
    return jsonify({"purchases": purchases, "total": total, "page": page})


@purchase_bp.route("/<int:purchase_id>", methods=["GET"])
@login_required
def get_purchase(purchase_id):
    p = purchase_model.get_by_id(purchase_id)
    if not p:
        return jsonify({"error": "Purchase not found"}), 404
    return jsonify(p)


@purchase_bp.route("/", methods=["POST"])
@login_required
def create_purchase():
    data = request.get_json()
    supplier_id = data.get("supplier_id")
    items = data.get("items", [])
    if not supplier_id:
        return jsonify({"error": "supplier_id is required"}), 400
    if not items:
        return jsonify({"error": "At least one item required"}), 400
    for item in items:
        if not item.get("product_id") or int(item.get("quantity", 0)) <= 0:
            return jsonify({"error": "Each item needs product_id and quantity > 0"}), 400

    purchase_date = data.get("purchase_date", str(date.today()))
    notes = data.get("notes", "")
    created_by = session.get("user_id")

    purchase_id = purchase_model.create_purchase(
        supplier_id, items, notes, created_by, purchase_date
    )
    return jsonify({"id": purchase_id, "message": "Purchase recorded"}), 201


@purchase_bp.route("/export", methods=["GET"])
@login_required
def export():
    purchases, _ = purchase_model.get_all(page=1, per_page=10000,
                                           start_date=request.args.get("start_date"),
                                           end_date=request.args.get("end_date"))
    headers = ["id", "supplier_name", "total_amount", "purchase_date", "created_by_name"]
    return export_csv(headers, purchases, "purchases.csv")