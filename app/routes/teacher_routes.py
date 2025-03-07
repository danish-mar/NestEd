from flask import Blueprint, request, jsonify
from app.modules.teacher_module import TeacherModule
from app.modules.student_module import StudentModule
from app.modules.marks_module import MarksModule
from auth_decorator import login_required

teacher_blueprint = Blueprint("teacher", __name__)

# -------------------- Teacher Authentication --------------------
@teacher_blueprint.route("/login", methods=["POST"])
def teacher_login():
    data = request.json
    session_id = TeacherModule.login(data["email"], data["password"])
    if session_id:
        return jsonify({"success": True, "session_id": session_id})
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

# -------------------- View Students --------------------
@teacher_blueprint.route("/students", methods=["GET"])
@login_required
def list_students():
    students = StudentModule.get_all_students()
    return jsonify([student.serialize() for student in students])

# -------------------- View Marks --------------------
@teacher_blueprint.route("/students/<int:student_id>/marks", methods=["GET"])
@login_required
def get_student_marks(student_id):
    marks = MarksModule.get_student_marks(student_id)
    return jsonify([mark.serialize() for mark in marks])

# -------------------- Assign Marks --------------------
@teacher_blueprint.route("/students/<int:student_id>/marks", methods=["POST"])
@login_required
def assign_marks(student_id):
    data = request.json
    teacher_id = request.cookies.get("user_id")  # Get teacher ID from session

    # Ensure teacher can only assign marks for their subject
    subject_id = TeacherModule.get_subject_id(teacher_id)
    if not subject_id:
        return jsonify({"error": "Unauthorized to assign marks"}), 403

    new_marks = MarksModule.assign_marks(student_id, subject_id, teacher_id, data["d1_oral"], data["d2_practical"], data["d3_theory"])
    return jsonify({"success": True, "marks_id": new_marks.marks_id})
