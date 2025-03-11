import os

from flask import Blueprint, request, jsonify, send_file
from app.modules.hod_module import HODModule
from app.modules.reporting_module import ReportingModule
from app.modules.teacher_module import TeacherModule
from app.modules.subject_module import SubjectModule
from app.modules.student_module import StudentModule
from app.modules.marks_module import MarksModule
from app.modules.session_manager import SessionManager
from app.modules.middleware import hod_login_required as login_required

hod_blueprint = Blueprint("hod", __name__)


# -------------------- HOD Authentication --------------------
@hod_blueprint.route("/login", methods=["POST"])
def hod_login():
    data = request.json
    email_id = data["email"]
    password = data["password"]

    hod_object = HODModule.login(email_id, password)
    if hod_object:
        session_id = SessionManager.create_session(hod_object.hod_id, role="hod")
        response = jsonify({"success": True, "hod_object": hod_object.serialize()})
        response.set_cookie("session_id", session_id, httponly=True, secure=True)
        return response
    return jsonify({"success": False, "error": "Invalid credentials"}), 401


@hod_blueprint.route("/logout", methods=["POST"])
@login_required
def hod_logout():
    session_id = request.cookies.get("session_id")
    SessionManager.delete_session(session_id)
    response = jsonify({"success": True})
    response.set_cookie("session_id", "", expires=0)
    return response


# -------------------- Manage Teachers --------------------
@hod_blueprint.route("/teachers", methods=["POST"])
@login_required
def create_teacher():
    data = request.json
    teacher = TeacherModule.create_teacher(
        data["name"], data["email"], data["phone"], data["password"], data["subject_id"]
    )
    return jsonify({"success": True, "teacher_id": teacher.teacher_id})


@hod_blueprint.route("/teachers", methods=["GET"])
@login_required
def list_teachers():
    teachers = TeacherModule.get_all_teachers()
    return jsonify([teacher.serialize() for teacher in teachers])


@hod_blueprint.route("/teachers/<int:teacher_id>", methods=["DELETE"])
@login_required
def delete_teacher(teacher_id):
    success = TeacherModule.delete_teacher(teacher_id)
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "Teacher not found"}), 404


@hod_blueprint.route("/teachers/<int:teacher_id>", methods=["PUT"])
@login_required
def update_teacher(teacher_id):
    data = request.json
    teacher = TeacherModule.update_teacher(teacher_id, **data)
    if teacher:
        return jsonify({"success": True, "teacher": teacher.serialize()})
    return jsonify({"error": "Teacher not found"}), 404


# -------------------- Manage Subjects --------------------
@hod_blueprint.route("/subjects", methods=["POST"])
@login_required
def create_subject():
    data = request.json
    subject = SubjectModule.create_subject(data["subject_name"])
    return jsonify({"success": True, "subject_id": subject.subject_id})


@hod_blueprint.route("/subjects", methods=["GET"])
@login_required
def list_subjects():
    subjects = SubjectModule.get_all_subjects()
    return jsonify([subject.serialize() for subject in subjects])


@hod_blueprint.route("/subjects/<int:subject_id>", methods=["DELETE"])
@login_required
def delete_subject(subject_id):
    success = SubjectModule.delete_subject(subject_id)
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "Subject not found"}), 404


@hod_blueprint.route("/subjects/<int:subject_id>", methods=["PUT"])
@login_required
def update_subject(subject_id):
    data = request.json
    subject = SubjectModule.update_subject(subject_id, data["subject_name"])
    if subject:
        return jsonify({"success": True, "subject": subject.serialize()})
    return jsonify({"error": "Subject not found"}), 404


# -------------------- Manage Students --------------------
@hod_blueprint.route("/students", methods=["POST"])
@login_required
def create_student():
    data = request.json
    student = StudentModule.create_student(
        data["name"], data["email"], data["phone"], data["dob"], data["gender"], data["address"], data["admission_year"]
    )
    return jsonify({"success": True, "student_id": student.student_id})


@hod_blueprint.route("/students", methods=["GET"])
@login_required
def list_students():
    students = StudentModule.get_all_students()
    return jsonify([student.serialize() for student in students])


@hod_blueprint.route("/students/<int:student_id>", methods=["DELETE"])
@login_required
def delete_student(student_id):
    success = StudentModule.delete_student(student_id)
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "Student not found"}), 404


@hod_blueprint.route("/students/<int:student_id>", methods=["GET"])
@login_required
def get_student(student_id):
    student = StudentModule.get_student_by_id(student_id)
    if student:
        return jsonify(student.serialize())
    return jsonify({"error": "Student not found"}), 404


@hod_blueprint.route("/students/<int:student_id>", methods=["PUT"])
@login_required
def update_student(student_id):
    data = request.json
    student = StudentModule.update_student(student_id, **data)
    if student:
        return jsonify({"success": True, "student": student.serialize()})
    return jsonify({"error": "Student not found"}), 404


@hod_blueprint.route("/students/<int:student_id>/marks", methods=["GET"])
@login_required
def get_student_marks(student_id):
    marks = MarksModule.get_student_marks(student_id)
    return jsonify([mark.serialize() for mark in marks])


# -------------------- View Marks -------------------- #
@hod_blueprint.route("/marks", methods=["GET"])
@login_required
def view_marks():
    marks = MarksModule.get_all_marks()
    return jsonify([mark.serialize() for mark in marks])


# -------------------- Reporting Routes--------------- #

@hod_blueprint.route("/report/students", methods=["GET"])
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


@hod_blueprint.route("/report/student/<int:student_id>", methods=["GET"])
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
