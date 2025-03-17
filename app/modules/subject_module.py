from app.models import Subject
from app.extensions import db


class SubjectModule:
    @staticmethod
    def create_subject(subject_name, year):
        """Creates a new subject"""
        new_subject = Subject(subject_name=subject_name, year=year)
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

    @staticmethod
    def update_subject(subject_id, new_subject_name):
        """Update subject name"""
        subject = Subject.query.get(subject_id)
        if subject:
            subject.subject_name = new_subject_name
            db.session.commit()
            return subject
        return None
