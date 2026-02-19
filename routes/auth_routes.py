from flask import Blueprint, request, jsonify, session
from services.auth import login_user, register_user, get_current_user, admin_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password required"}), 400
    user = login_user(data["username"], data["password"])
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    session.permanent = True
    session["user_id"] = user["id"]
    session["role"] = user["role"]
    return jsonify({"message": "Login successful", "user": {"id": user["id"], "username": user["username"], "role": user["role"]}})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@auth_bp.route("/me", methods=["GET"])
def me():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify(user)


@auth_bp.route("/register", methods=["POST"])
@admin_required
def register():
    data = request.get_json()
    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password required"}), 400
    role = data.get("role", "staff")
    if role not in ("admin", "staff"):
        return jsonify({"error": "Invalid role"}), 400
    try:
        user_id = register_user(data["username"], data["password"], role)
        return jsonify({"id": user_id, "message": "User created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400