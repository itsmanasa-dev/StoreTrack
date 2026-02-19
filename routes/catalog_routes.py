from flask import Blueprint, request, jsonify
from models import category as cat_model
from models import supplier as sup_model
from services.auth import login_required, admin_required

category_bp = Blueprint("categories", __name__, url_prefix="/api/categories")
supplier_bp = Blueprint("suppliers", __name__, url_prefix="/api/suppliers")


@category_bp.route("/", methods=["GET"])
@login_required
def list_categories():
    return jsonify(cat_model.get_all())


@category_bp.route("/", methods=["POST"])
@admin_required
def create_category():
    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    cat_id = cat_model.create(data["name"])
    return jsonify({"id": cat_id}), 201


@category_bp.route("/<int:cat_id>", methods=["DELETE"])
@admin_required
def delete_category(cat_id):
    rows = cat_model.delete(cat_id)
    if not rows:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"})


@supplier_bp.route("/", methods=["GET"])
@login_required
def list_suppliers():
    return jsonify(sup_model.get_all())


@supplier_bp.route("/", methods=["POST"])
@admin_required
def create_supplier():
    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    sup_id = sup_model.create(data)
    return jsonify({"id": sup_id}), 201


@supplier_bp.route("/<int:sup_id>", methods=["PUT"])
@admin_required
def update_supplier(sup_id):
    data = request.get_json()
    rows = sup_model.update(sup_id, data)
    if not rows:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Updated"})


@supplier_bp.route("/<int:sup_id>", methods=["DELETE"])
@admin_required
def delete_supplier(sup_id):
    rows = sup_model.delete(sup_id)
    if not rows:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"})