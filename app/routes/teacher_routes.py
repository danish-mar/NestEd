import os

from flask import Blueprint, request, jsonify, send_file

from app.modules.reporting_module import ReportingModule
from app.modules.session_manager import SessionManager
from app.modules.teacher_module import TeacherModule
from app.modules.student_module import StudentModule
from app.modules.marks_module import MarksModule
from app.modules.middleware import teacher_login_required as login_required, teacher_login_required

teacher_blueprint = Blueprint("teacher", __name__)


# -------------------- Teacher Authentication --------------------
@teacher_blueprint.route("/login", methods=["POST"])
def teacher_login():
    data = request.json
    email = data["email"]
    password = data["password"]
    teacher = TeacherModule.get_teacher_by_email(email)
    if teacher and teacher.check_password(password):
        session_id = SessionManager.create_session(user_id=teacher.teacher_id, role="teacher")
        if session_id:
            response = jsonify({"success": True})
            response.set_cookie("session_id", session_id, httponly=True, secure=True)
            return response
        else:
            return jsonify({"success": False, "error": "Session creation failed"}), 500
    else:
        return jsonify({"success": False, "error": "Invalid credentials"}), 401


# -------------------- View Students --------------------
@teacher_blueprint.route("/students", methods=["GET"])
@teacher_login_required
def list_students():
    students = StudentModule.get_all_students()
    return jsonify([student.serialize() for student in students])


# -------------------- View Marks --------------------
@teacher_blueprint.route("/students/<int:student_id>/marks", methods=["GET"])
@teacher_login_required
def get_student_marks(student_id):
    marks = MarksModule.get_student_marks(student_id)
    return jsonify([mark.serialize() for mark in marks])


# -------------------- Assign Marks --------------------
@teacher_blueprint.route("/students/<int:student_id>/marks", methods=["POST"])
@teacher_login_required
def assign_marks(student_id):
    data = request.json

    # Ensure teacher can only assign marks for their subject
    teacher_id = SessionManager.get_user_id_from_session_id(request.cookies.get("session_id"), role="teacher")
    subject_id = TeacherModule.get_teacher_by_id(teacher_id).subject_id

    # wrote this one liner for idk what reasons but i prefer readability over one liners subject_id =
    # TeacherModule.get_teacher_by_id(SessionManager.get_user_id_from_session_id(request.cookies.get("session_id"),
    # role="teacher")).subject_id
    if not subject_id:
        return jsonify({"error": "Unauthorized to assign marks"}), 403

    new_marks = MarksModule.assign_marks(student_id, subject_id, data["d1_oral"], data["d2_practical"],
                                         data["d3_theory"])
    return jsonify({"success": True, "marks_id": new_marks.marks_id})


@teacher_blueprint.route("/report/students", methods=["GET"])
@login_required
def download_student_report():
    """Download all students' details and marks report"""
    file_format = request.args.get("format", "excel")  # Default to Excel
    if file_format not in ["excel", "pdf"]:
        return jsonify({"error": "Invalid format. Use 'excel' or 'pdf'."}), 400

    file_path = ReportingModule.generate_student_report(file_format)

    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Report generation failed"}), 500

    return send_file(file_path, as_attachment=True)


@teacher_blueprint.route("/report/student/<int:student_id>", methods=["GET"])
@login_required
def download_single_student_report(student_id):
    """Download report for a single student with all their marks"""
    file_format = request.args.get("format", "excel")  # Default to Excel
    if file_format not in ["excel", "pdf"]:
        return jsonify({"error": "Invalid format. Use 'excel' or 'pdf'."}), 400

    file_path = ReportingModule.generate_single_student_report(student_id, file_format)

    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Student not found or report generation failed"}), 404

    return send_file(file_path, as_attachment=True)
