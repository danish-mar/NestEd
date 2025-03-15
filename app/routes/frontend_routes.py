from flask import Blueprint, render_template, jsonify, request

from app.modules.middleware import hod_login_required, teacher_login_required
from app.modules.session_manager import SessionManager

frontend_blueprint = Blueprint("frontend", __name__)


@frontend_blueprint.route("/")
def home():
    return render_template("index.html")


@frontend_blueprint.route("/login/hod")
def hod_login():
    return render_template("login_hod.html")


@frontend_blueprint.route("/login/teacher")
def teacher_login():
    return render_template("login_teacher.html")


# hod related routes

@frontend_blueprint.route("/dashboard/hod")
@hod_login_required
def hod_dashboard():
    return render_template("hod_dashboard.html")


@frontend_blueprint.route("/dashboard/hod/manage/teacher")
@hod_login_required
def hod_dashboard_manage_teachers():
    return render_template("hod_teachers.html")


@frontend_blueprint.route("/dashboard/hod/manage/subjects")
@hod_login_required
def hod_dashboard_manage_subjects():
    return render_template("hod_subjects.html")


@frontend_blueprint.route("/dashboard/hod/manage/students")
@hod_login_required
def hod_dashboard_manage_students():
    return render_template("hod_students.html")


@frontend_blueprint.route("/dashboard/hod/view/marks")
@hod_login_required
def hod_dashboard_view_marks():
    return render_template("hod_marks.html")


@frontend_blueprint.route("/dashboard/teacher")
@teacher_login_required
def teacher_dashboard():
    return render_template("teacher_dashboard.html")


@frontend_blueprint.route("/dashboard/teacher/manage/students")
@teacher_login_required
def teacher_dashboard_manage_students():
    return render_template("teacher_students.html")


@frontend_blueprint.route("/dashboard/teacher/manage/marks")
@teacher_login_required
def teacher_dashboard_view_marks():
    return render_template("teacher_assign_marks.html")


@frontend_blueprint.route("/logout")
@hod_login_required
def logout_hod():
    """Logs out the user by clearing session from backend and frontend"""
    session_id = request.cookies.get("session_id")

    # If session exists, remove it from SessionManager
    if session_id:
        SessionManager.delete_session(session_id)  # Remove session from memory

    response = render_template("logout_hod.html")  # Load logout page
    return response


@frontend_blueprint.route("/dashboard/teacher/view/subjects")
@teacher_login_required
def teacher_dashboard_view_subjects():
    return render_template("teacher_subjects.html")
