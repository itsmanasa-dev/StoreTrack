from functools import wraps
from flask import session, jsonify, redirect, url_for
from database.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash


def login_user(username, password):
    with get_db() as (_, cursor):
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND is_active = TRUE",
            (username,),
        )
        user = cursor.fetchone()
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


def register_user(username, password, role="staff"):
    with get_db() as (_, cursor):
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
            (username, generate_password_hash(password), role),
        )
        return cursor.lastrowid


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    with get_db() as (_, cursor):
        cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            if _wants_json():
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user or user["role"] != "admin":
            if _wants_json():
                return jsonify({"error": "Admin access required"}), 403
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def _wants_json():
    from flask import request
    return request.is_json or request.headers.get("Accept", "").find("application/json") != -1