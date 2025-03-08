from functools import wraps
from flask import request, redirect, url_for, jsonify
from app.modules.session_manager import SessionManager
from urllib.parse import quote


def teacher_login_required(func):
    """Middleware to check authentication via session."""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        session_id = request.cookies.get("session_id")
        user_id = SessionManager.get_user_id_from_session_id(session_id, role="teacher") if session_id else None

        if not user_id:
            if request.method == "GET":
                redirect_url = quote(request.full_path)
                return redirect(url_for('login', redirect=redirect_url))
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        return func(*args, **kwargs)

    return decorated_function


def hod_login_required(func):
    """Middleware to check HOD authentication via session."""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        session_id = request.cookies.get("session_id")
        user_id = SessionManager.get_user_id_from_session_id(session_id, role="hod") if session_id else None

        if not user_id:
            if request.method == "GET":
                redirect_url = quote(request.path)
                return redirect(url_for('frontend.hod_login', redirect=redirect_url))
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        return func(*args, **kwargs)

    return decorated_function
