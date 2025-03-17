from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from flask_bcrypt import Bcrypt
from app.extensions import db, bcrypt


# ---------------------------- MODULE 1: HOD ----------------------------
class HOD(db.Model):
    """HOD (Head of Department) manages everything"""
    __tablename__ = "hod"
    hod_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # Password for login

    def set_password(self, password):
        """Hashes the password before storing"""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        """Verifies the entered password"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def serialize(self):
        """Convert SQLAlchemy object to a dictionary"""
        return {
            "hod_id": self.hod_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone
        }


# ---------------------------- MODULE 2: TEACHERS ----------------------------
class Teacher(db.Model):
    """Teachers are assigned subjects by the HOD and manage marks"""
    __tablename__ = "teachers"
    teacher_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # Password for login
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)  # Assigned subject

    subject = relationship("Subject")

    def set_password(self, password):
        """Hashes the password before storing"""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        """Verifies the entered password"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def serialize(self):
        """Convert SQLAlchemy object to a dictionary"""
        return {
            "teacher_id": self.teacher_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "subject": self.subject.serialize() if self.subject else None
        }


# ---------------------------- MODULE 3: SUBJECTS ----------------------------
class Subject(db.Model):
    """Subjects are assigned to teachers by the HOD"""
    __tablename__ = "subjects"
    subject_id = Column(Integer, primary_key=True)
    subject_name = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)

    def serialize(self):
        """Convert SQLAlchemy object to a dictionary"""
        return {
            "subject_id": self.subject_id,
            "subject_name": self.subject_name,
            "year": self.year
        }


# ---------------------------- MODULE 4: STUDENTS ----------------------------
class Student(db.Model):
    """Stores student information"""
    __tablename__ = "students"
    student_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    dob = Column(String(20), nullable=False)
    gender = Column(String(10), nullable=False)
    address = Column(String(255), nullable=False)
    current_year = Column(Integer, nullable=False, default=1)
    admission_year = Column(Integer, nullable=False)

    def serialize(self):
        """Convert SQLAlchemy object to a dictionary"""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "dob": self.dob,
            "gender": self.gender,
            "address": self.address,
            "admission_year": self.admission_year,
            "current_year": self.current_year
        }


# ---------------------------- MODULE 5: MANUAL MARKS (EXPERIMENTS) ----------------------------
class ManualMarks(db.Model):
    """Stores experiment marks for students dynamically"""
    __tablename__ = "manual_marks"
    manual_marks_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    experiment_number = Column(Integer, nullable=False)  # E1-E32 as numbers (1-32)
    marks_obtained = Column(Float, default=0)

    student = relationship("Student")
    subject = relationship("Subject")

    @staticmethod
    def calculate_total(student_id, subject_id):
        """Calculate total experiment marks for a student in a subject"""
        experiments = db.session.query(ManualMarks).filter_by(student_id=student_id, subject_id=subject_id).all()
        total_exp_marks = sum(exp.marks_obtained for exp in experiments)
        return total_exp_marks

    def serialize(self):
        """Convert to dictionary"""
        return {
            "manual_marks_id": self.manual_marks_id,
            "student_id": self.student_id,
            "subject_id": self.subject_id,
            "experiment_number": self.experiment_number,
            "marks_obtained": self.marks_obtained
        }


# ---------------------------- MODULE 6: PRACTICAL EXAM MARKS ----------------------------
class PracticalMarks(db.Model):
    """Stores practical exam marks for students"""
    __tablename__ = "practical_marks"
    practical_marks_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    practical_exam_marks = Column(Float, nullable=False, default=0)

    student = relationship("Student")
    subject = relationship("Subject")

    def serialize(self):
        """Convert to dictionary"""
        return {
            "practical_marks_id": self.practical_marks_id,
            "student": self.student.serialize(),
            "subject": self.subject.serialize(),
            "practical_exam_marks": self.practical_exam_marks
        }


# ---------------------------- MODULE 7: CLASS TEST MARKS ----------------------------
class ClassTestMarks(db.Model):
    """Stores marks for Class Test 1 and Class Test 2"""
    __tablename__ = "class_test_marks"
    class_test_marks_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    class_test_1 = Column(Float, default=0)
    class_test_2 = Column(Float, default=0)

    student = relationship("Student")
    subject = relationship("Subject")

    def calculate_average(self):
        """Calculate average of class test 1 & 2"""
        return (self.class_test_1 + self.class_test_2) / 2

    def serialize(self):
        """Convert to dictionary"""
        return {
            "class_test_marks_id": self.class_test_marks_id,
            "student": self.student.serialize(),
            "subject": self.subject.serialize(),
            "class_test_1": self.class_test_1,
            "class_test_2": self.class_test_2,
            "average_marks": self.calculate_average()
        }


# ---------------------------- MODULE 8: SLA ACTIVITY MARKS ----------------------------
class SLAMarks(db.Model):
    """Stores SLA marks (Micro Projects, Assignments, Others)"""
    __tablename__ = "sla_marks"
    sla_marks_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    micro_project = Column(Float, default=0)
    assignment = Column(Float, default=0)
    other_marks = Column(Float, default=0)

    student = relationship("Student")
    subject = relationship("Subject")

    def serialize(self):
        """Convert to dictionary"""
        return {
            "sla_marks_id": self.sla_marks_id,
            "student": self.student.serialize(),
            "subject": self.subject.serialize(),
            "micro_project": self.micro_project,
            "assignment": self.assignment,
            "other_marks": self.other_marks
        }