from flask import Blueprint, render_template

frontend_blueprint = Blueprint("frontend", __name__)

@frontend_blueprint.route("/")
def home():
    return render_template("index.html")

@frontend_blueprint.route("/login/hod")
def hod_login():
    return render_template("hod_login.html")

@frontend_blueprint.route("/login/teacher")
def teacher_login():
    return render_template("teacher_login.html")

@frontend_blueprint.route("/dashboard/hod")
def hod_dashboard():
    return render_template("hod_dashboard.html")

@frontend_blueprint.route("/dashboard/teacher")
def teacher_dashboard():
    return render_template("teacher_dashboard.html")
