from app.models import Student
from app.extensions import db


class StudentModule:
    @staticmethod
    def create_student(name, email, phone, dob, gender, address, admission_year, current_year): #add current year
        """Creates a new student"""
        new_student = Student(name=name, email=email, phone=phone, dob=dob, gender=gender,
                              address=address, admission_year=admission_year, current_year=current_year) #add current year
        db.session.add(new_student)
        db.session.commit()
        return new_student

    @staticmethod
    def get_all_students():
        """Returns all students"""
        return Student.query.all()

    @staticmethod
    def get_student_by_id(student_id):
        """Fetch student by ID"""
        return Student.query.get(student_id)

    @staticmethod
    def delete_student(student_id):
        """Delete a student"""
        student = Student.query.get(student_id)
        if student:
            db.session.delete(student)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update_student(student_id, **kwargs):
        """Updates student details"""
        student = Student.query.get(student_id)
        if not student:
            return None
        for key, value in kwargs.items():
            if hasattr(student, key):
                setattr(student, key, value)
        db.session.commit()
        return student