from flask import Blueprint, request, jsonify
from models import product as product_model
from services.auth import login_required, admin_required
from services.export import export_csv

product_bp = Blueprint("products", __name__, url_prefix="/api/products")


def _validate_product(data):
    errors = []
    if not data.get("name", "").strip():
        errors.append("Product name is required.")
    try:
        cost = float(data.get("cost_price", -1))
        sell = float(data.get("selling_price", -1))
        if cost < 0:
            errors.append("cost_price must be >= 0.")
        if sell < 0:
            errors.append("selling_price must be >= 0.")
    except (TypeError, ValueError):
        errors.append("cost_price and selling_price must be numeric.")
    if not data.get("category_id"):
        errors.append("category_id is required.")
    return errors


@product_bp.route("/", methods=["GET"])
@login_required
def list_products():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    search = request.args.get("search")
    category_id = request.args.get("category_id", type=int)
    products, total = product_model.get_all(page, per_page, search, category_id)
    return jsonify({"products": products, "total": total, "page": page, "pages": -(-total // per_page)})


@product_bp.route("/<int:product_id>", methods=["GET"])
@login_required
def get_product(product_id):
    p = product_model.get_by_id(product_id)
    if not p:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(p)


@product_bp.route("/barcode/<barcode>", methods=["GET"])
@login_required
def get_by_barcode(barcode):
    p = product_model.get_by_barcode(barcode)
    if not p:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(p)


@product_bp.route("/", methods=["POST"])
@login_required
def create_product():
    data = request.get_json()
    errors = _validate_product(data)
    if errors:
        return jsonify({"errors": errors}), 400
    product_id = product_model.create(data)
    return jsonify({"id": product_id, "message": "Product created"}), 201


@product_bp.route("/<int:product_id>", methods=["PUT"])
@login_required
def update_product(product_id):
    data = request.get_json()
    errors = _validate_product(data)
    if errors:
        return jsonify({"errors": errors}), 400
    rows = product_model.update(product_id, data)
    if not rows:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"message": "Updated"})


@product_bp.route("/<int:product_id>", methods=["DELETE"])
@admin_required
def delete_product(product_id):
    rows = product_model.delete(product_id)
    if not rows:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"message": "Deleted"})


@product_bp.route("/low-stock", methods=["GET"])
@login_required
def low_stock():
    return jsonify(product_model.get_low_stock())


@product_bp.route("/export", methods=["GET"])
@login_required
def export():
    products, _ = product_model.get_all(page=1, per_page=10000)
    headers = ["id", "name", "category_name", "cost_price", "selling_price",
               "stock_quantity", "minimum_stock_level", "barcode"]
    return export_csv(headers, products, "products.csv")