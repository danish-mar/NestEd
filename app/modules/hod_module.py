from app.models import HOD
from app.extensions import db

class HODModule:
    @staticmethod
    def create_hod(name, email, phone, password):
        """Creates a new HOD"""
        new_hod = HOD(name=name, email=email, phone=phone)
        new_hod.set_password(password)
        db.session.add(new_hod)
        db.session.commit()
        return new_hod

    @staticmethod
    def get_all_hods():
        """Returns all HODs"""
        return HOD.query.all()

    @staticmethod
    def get_hod_by_id(hod_id):
        """Fetch HOD by ID"""
        return HOD.query.get(hod_id)

    @staticmethod
    def delete_hod(hod_id):
        """Delete an HOD"""
        hod = HOD.query.get(hod_id)
        if hod:
            db.session.delete(hod)
            db.session.commit()
            return True
        return False
