from flask import Blueprint, request, jsonify
from app.modules.hod_module import HODModule
from app.modules.teacher_module import TeacherModule
from app.modules.subject_module import SubjectModule
from app.modules.student_module import StudentModule
from app.modules.marks_module import MarksModule
from app.modules.session_manager import SessionManager

hod_blueprint = Blueprint("hod", __name__)

# -------------------- HOD Authentication --------------------
@hod_blueprint.route("/login", methods=["POST"])
def hod_login():
    data = request.json
    session_id = HODModule.login(data["email"], data["password"])
    if session_id:
        return jsonify({"success": True, "session_id": session_id})
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

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

# -------------------- Manage Students --------------------
@hod_blueprint.route("/students", methods=["POST"])
@login_required
def create_student():
    data = request.json
    student = StudentModule.create_student(
        data["name"], data["email"], data["phone"], data["dob"], data["gender"], data["address"], data["admission_year"]
    )
    return jsonify({"success": True, "student_id": student.student_id})

@hod_blueprint.route("/students/<int:student_id>", methods=["GET"])
@login_required
def get_student(student_id):
    student = StudentModule.get_student_by_id(student_id)
    return jsonify(student.serialize()) if student else jsonify({"error": "Student not found"}), 404

@hod_blueprint.route("/students/<int:student_id>/marks", methods=["GET"])
@login_required
def get_student_marks(student_id):
    marks = MarksModule.get_student_marks(student_id)
    return jsonify([mark.serialize() for mark in marks])
