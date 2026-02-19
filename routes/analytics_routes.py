from flask import Blueprint, request, jsonify
from services import analytics
from services.auth import login_required
from services.export import export_csv

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@analytics_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return jsonify(analytics.get_dashboard_stats())


@analytics_bp.route("/profit-report", methods=["GET"])
@login_required
def profit_report():
    start = request.args.get("start_date")
    end = request.args.get("end_date")
    group_by = request.args.get("group_by", "day")
    if not start or not end:
        return jsonify({"error": "start_date and end_date are required"}), 400
    data = analytics.get_profit_report(start, end, group_by)
    return jsonify(data)


@analytics_bp.route("/profit-report/export", methods=["GET"])
@login_required
def export_profit():
    start = request.args.get("start_date")
    end = request.args.get("end_date")
    group_by = request.args.get("group_by", "day")
    data = analytics.get_profit_report(start, end, group_by)
    headers = ["period", "revenue", "cost", "profit", "num_sales"]
    return export_csv(headers, data, f"profit_{start}_{end}.csv")


@analytics_bp.route("/reorder-suggestions", methods=["GET"])
@login_required
def reorder_suggestions():
    return jsonify(analytics.get_reorder_suggestions())