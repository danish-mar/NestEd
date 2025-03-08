from app.models import Marks
from app.extensions import db

class MarksModule:
    @staticmethod
    def assign_marks(student_id, subject_id, d1_oral, d2_practical, d3_theory):
        """Assign marks to a student"""
        new_marks = Marks(student_id=student_id, subject_id=subject_id,
                          d1_oral=d1_oral, d2_practical=d2_practical, d3_theory=d3_theory)
        new_marks.calculate_total()
        db.session.add(new_marks)
        db.session.commit()
        return new_marks

    @staticmethod
    def get_student_marks(student_id):
        """Fetch all marks of a student"""
        return Marks.query.filter_by(student_id=student_id).all()

    @staticmethod
    def update_marks(marks_id, d1_oral, d2_practical, d3_theory):
        """Update marks of a student"""
        marks = Marks.query.get(marks_id)
        if marks:
            marks.d1_oral = d1_oral
            marks.d2_practical = d2_practical
            marks.d3_theory = d3_theory
            marks.calculate_total()
            db.session.commit()
            return marks
        return None

    @staticmethod
    def delete_marks(marks_id):
        """Delete marks of a student"""
        marks = Marks.query.get(marks_id)
        if marks:
            db.session.delete(marks)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_all_marks():
        """Returns all marks"""
        return Marks.query.all()
