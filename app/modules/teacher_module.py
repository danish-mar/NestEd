from app.models import Teacher
from app.extensions import db

class TeacherModule:
    @staticmethod
    def create_teacher(name, email, phone, password, subject_id):
        """Creates a new teacher with an assigned subject"""
        new_teacher = Teacher(name=name, email=email, phone=phone, subject_id=subject_id)
        new_teacher.set_password(password)
        db.session.add(new_teacher)
        db.session.commit()
        return new_teacher

    @staticmethod
    def get_all_teachers():
        """Returns all teachers"""
        return Teacher.query.all()

    @staticmethod
    def get_teacher_by_id(teacher_id):
        """Fetch teacher by ID"""
        return Teacher.query.get(teacher_id)

    @staticmethod
    def get_teacher_by_email(email):
        """Fetch teacher by email"""
        return Teacher.query.filter_by(email=email).first()

    @staticmethod
    def delete_teacher(teacher_id):
        """Delete a teacher"""
        teacher = Teacher.query.get(teacher_id)
        if teacher:
            db.session.delete(teacher)
            db.session.commit()
            return True
        return False
