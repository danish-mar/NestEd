from app.models import Subject
from app.extensions import db

class SubjectModule:
    @staticmethod
    def create_subject(subject_name):
        """Creates a new subject"""
        new_subject = Subject(subject_name=subject_name)
        db.session.add(new_subject)
        db.session.commit()
        return new_subject

    @staticmethod
    def get_all_subjects():
        """Returns all subjects"""
        return Subject.query.all()

    @staticmethod
    def get_subject_by_id(subject_id):
        """Fetch subject by ID"""
        return Subject.query.get(subject_id)

    @staticmethod
    def delete_subject(subject_id):
        """Delete a subject"""
        subject = Subject.query.get(subject_id)
        if subject:
            db.session.delete(subject)
            db.session.commit()
            return True
        return False
