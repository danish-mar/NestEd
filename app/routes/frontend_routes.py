from flask import Blueprint, render_template

from app.modules.middleware import hod_login_required

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
def teacher_dashboard():
    return render_template("teacher_dashboard.html")
