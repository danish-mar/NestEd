import os

from flask import Blueprint, request, jsonify, send_file

from app.models import Subject, Student
from app.modules.reporting_module import ReportingModule
from app.modules.session_manager import SessionManager
from app.modules.teacher_module import TeacherModule
from app.modules.student_module import StudentModule
from app.modules.marks_module import MarksModule
from app.modules.middleware import teacher_login_required as login_required, teacher_login_required

teacher_blueprint = Blueprint("teacher", __name__)

# Helper function to get subject ID for a teacher
def get_teacher_subject_id(request):
    teacher_id = SessionManager.get_user_id_from_session_id(request.cookies.get("session_id"), role="teacher")
    if teacher_id:
        teacher = TeacherModule.get_teacher_by_id(teacher_id)
        if teacher:
            return teacher.subject_id
    return None

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


@teacher_blueprint.route("/students", methods=["GET"])
@teacher_login_required
def list_students():
    subject_id = get_teacher_subject_id(request)
    if not subject_id:
        return jsonify({"error": "Unauthorized or subject not found"}), 403

    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({"error": "Subject not found"}), 404

    students = Student.query.filter_by(current_year=subject.year).all() #filter students

    return jsonify([student.serialize() for student in students])





# -------------------- Manual Marks (Experiments) --------------------
@teacher_blueprint.route("/students/<int:student_id>/manual_marks", methods=["GET"])
@teacher_login_required
def get_manual_marks(student_id):
    subject_id = get_teacher_subject_id(request)
    if not subject_id:
        return jsonify({"error": "Unauthorized or subject not found"}), 403

    marks = MarksModule.get_manual_marks(student_id, subject_id)
    return jsonify([mark.serialize() for mark in marks])


@teacher_blueprint.route("/students/<int:student_id>/manual_marks", methods=["POST"])
@teacher_login_required
def assign_manual_marks(student_id):
    data = request.json
    subject_id = get_teacher_subject_id(request)
    if not subject_id:
        return jsonify({"error": "Unauthorized or subject not found"}), 403

    new_mark, error = MarksModule.assign_manual_mark(student_id, subject_id, data["experiment_number"],
                                                     data["marks_obtained"])
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "manual_marks_id": new_mark.manual_marks_id})


@teacher_blueprint.route("/manual_marks/<int:manual_marks_id>", methods=["PUT"])
@teacher_login_required
def update_manual_marks(manual_marks_id):
    data = request.json
    updated_mark, error = MarksModule.update_manual_mark(manual_marks_id, data["marks_obtained"])
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "manual_marks_id": updated_mark.manual_marks_id})


@teacher_blueprint.route("/manual_marks/<int:manual_marks_id>", methods=["DELETE"])
@teacher_login_required
def delete_manual_marks(manual_marks_id):
    success, error = MarksModule.delete_manual_mark(manual_marks_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": success})


# -------------------- Practical Exam Marks --------------------
@teacher_blueprint.route("/students/<int:student_id>/practical_marks", methods=["GET"])
@teacher_login_required
def get_practical_marks(student_id):
    subject_id = get_teacher_subject_id(request)
    if not subject_id:
        return jsonify({"error": "Unauthorized or subject not found"}), 403

    marks = MarksModule.get_practical_marks(student_id, subject_id)
    return jsonify(marks.serialize()) if marks else jsonify({"error": "Practical marks not found"}), 404


@teacher_blueprint.route("/students/<int:student_id>/practical_marks", methods=["POST"])
@teacher_login_required
def assign_practical_marks(student_id):
    data = request.json
    subject_id = get_teacher_subject_id(request)
    if not subject_id:
        return jsonify({"error": "Unauthorized or subject not found"}), 403

    new_mark, error = MarksModule.assign_practical_mark(student_id, subject_id, data["practical_exam_marks"])
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "practical_marks_id": new_mark.practical_marks_id})


@teacher_blueprint.route("/practical_marks/<int:practical_marks_id>", methods=["PUT"])
@teacher_login_required
def update_practical_marks(practical_marks_id):
    data = request.json
    updated_mark, error = MarksModule.update_practical_mark(practical_marks_id, data["practical_exam_marks"])
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "practical_marks_id": updated_mark.practical_marks_id})


@teacher_blueprint.route("/practical_marks/<int:practical_marks_id>", methods=["DELETE"])
@teacher_login_required
def delete_practical_marks(practical_marks_id):
    success, error = MarksModule.delete_practical_mark(practical_marks_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": success})


# -------------------- Class Test Marks --------------------
@teacher_blueprint.route("/students/<int:student_id>/class_test_marks", methods=["GET"])
@teacher_login_required
def get_class_test_marks(student_id):
    subject_id = get_teacher_subject_id(request)
    if not subject_id:
        return jsonify({"error": "Unauthorized or subject not found"}), 403

    marks = MarksModule.get_class_test_marks(student_id, subject_id)
    return jsonify(marks.serialize()) if marks else jsonify({"error": "Class test marks not found"}), 404


@teacher_blueprint.route("/students/<int:student_id>/class_test_marks", methods=["POST"])
@teacher_login_required
def assign_class_test_marks(student_id):
    data = request.json
    subject_id = get_teacher_subject_id(request)
    if not subject_id:
        return jsonify({"error": "Unauthorized or subject not found"}), 403

    print(data)

    new_marks, error = MarksModule.assign_class_test_marks(student_id, subject_id, data["class_test_1"],
                                                           data["class_test_2"])
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "class_test_marks_id": new_marks.class_test_marks_id})


@teacher_blueprint.route("/class_test_marks/<int:class_test_marks_id>", methods=["PUT"])
@teacher_login_required
def update_class_test_marks(class_test_marks_id):
    data = request.json
    updated_marks, error = MarksModule.update_class_test_marks(class_test_marks_id, data["class_test_1"],
                                                               data["class_test_2"])
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "class_test_marks_id": updated_marks.class_test_marks_id})


@teacher_blueprint.route("/class_test_marks/<int:class_test_marks_id>", methods=["DELETE"])
@teacher_login_required
def delete_class_test_marks(class_test_marks_id):
    success, error = MarksModule.delete_class_test_marks(class_test_marks_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": success})


# -------------------- SLA Activity Marks --------------------
@teacher_blueprint.route("/students/<int:student_id>/sla_marks", methods=["GET"])
@teacher_login_required
def get_sla_marks(student_id):
    subject_id = get_teacher_subject_id(request)
    if not subject_id:
        return jsonify({"error": "Unauthorized or subject not found"}), 403

    marks = MarksModule.get_sla_marks(student_id, subject_id)
    return jsonify(marks.serialize()) if marks else jsonify({"error": "SLA marks not found"}), 404


@teacher_blueprint.route("/students/<int:student_id>/sla_marks", methods=["POST"])
@teacher_login_required
def assign_sla_marks(student_id):
    data = request.json
    subject_id = get_teacher_subject_id(request)
    if not subject_id:
        return jsonify({"error": "Unauthorized or subject not found"}), 403

    new_marks, error = MarksModule.assign_sla_marks(student_id, subject_id, data["micro_project"], data["assignment"],
                                                    data["other_marks"])
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "sla_marks_id": new_marks.sla_marks_id})


@teacher_blueprint.route("/sla_marks/<int:sla_marks_id>", methods=["PUT"])
@teacher_login_required
def update_sla_marks(sla_marks_id):
    data = request.json
    updated_marks, error = MarksModule.update_sla_marks(sla_marks_id, data["micro_project"], data["assignment"],
                                                        data["other_marks"])
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "sla_marks_id": updated_marks.sla_marks_id})


@teacher_blueprint.route("/sla_marks/<int:sla_marks_id>", methods=["DELETE"])
@teacher_login_required
def delete_sla_marks(sla_marks_id):
    success, error = MarksModule.delete_sla_marks(sla_marks_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": success})


#
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


# -------------------- Get Teacher Details --------------------
@teacher_blueprint.route("/details", methods=["GET"])
@login_required
def get_teacher_details():
    session_id = request.cookies.get("session_id")
    teacher_id = SessionManager.get_user_id_from_session_id(session_id, role="teacher")
    teacher = TeacherModule.get_teacher_by_id(teacher_id)

    if teacher:
        return jsonify(teacher.serialize())
    else:
        return jsonify({"error": "Teacher not found"}), 404
