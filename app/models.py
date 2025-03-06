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

# ---------------------------- MODULE 3: SUBJECTS ----------------------------
class Subject(db.Model):
    """Subjects are assigned to teachers by the HOD"""
    __tablename__ = "subjects"
    subject_id = Column(Integer, primary_key=True)
    subject_name = Column(String(100), nullable=False)

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
    admission_year = Column(Integer, nullable=False)

# ---------------------------- MODULE 5: MARKS SYSTEM ----------------------------
class Marks(db.Model):
    """Stores marks for students in subjects assigned to teachers"""
    __tablename__ = "marks"
    marks_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"), nullable=False)  # Teacher managing the marks
    d1_oral = Column(Float, nullable=False, default=0)  # D1 - Oral Marks
    d2_practical = Column(Float, nullable=False, default=0)  # D2 - Practical Marks
    d3_theory = Column(Float, nullable=False, default=0)  # D3 - Theory Marks
    total_marks = Column(Float, nullable=False, default=0)  # Auto-calculated total

    student = relationship("Student")
    subject = relationship("Subject")
    teacher = relationship("Teacher")

    def calculate_total(self):
        """Calculates total marks"""
        self.total_marks = self.d1_oral + self.d2_practical + self.d3_theory
