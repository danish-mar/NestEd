from app.models import ManualMarks, PracticalMarks, ClassTestMarks, SLAMarks, Student, Subject
from app.extensions import db


class MarksModule:
    # Helper function to verify student and subject year
    @staticmethod
    def _verify_year(student_id, subject_id):
        """Verify if student and subject belong to the same year."""
        student = Student.query.get(student_id)
        subject = Subject.query.get(subject_id)

        if not student or not subject:
            return False, "Student or Subject not found."

        if student.current_year != subject.year:
            return False, "Student and Subject belong to different years."

        return True, None

    # -------------------- Manual Marks (Experiments) --------------------
    @staticmethod
    def assign_manual_mark(student_id, subject_id, experiment_number, marks_obtained):
        """Assign manual (experiment) marks for a student with year verification."""
        is_valid, error_message = MarksModule._verify_year(student_id, subject_id)
        if not is_valid:
            return None, error_message

        new_mark = ManualMarks(student_id=student_id, subject_id=subject_id,
                               experiment_number=experiment_number, marks_obtained=marks_obtained)
        db.session.add(new_mark)
        db.session.commit()
        return new_mark, None

    @staticmethod
    def get_manual_marks(student_id, subject_id):
        """Fetch all manual (experiment) marks of a student for a subject."""
        return ManualMarks.query.filter_by(student_id=student_id, subject_id=subject_id).all()

    @staticmethod
    def update_manual_mark(manual_marks_id, marks_obtained):
        """Update manual (experiment) marks for a student with year verification."""
        mark = ManualMarks.query.get(manual_marks_id)
        if not mark:
            return None, "Manual mark not found."

        is_valid, error_message = MarksModule._verify_year(mark.student_id, mark.subject_id)
        if not is_valid:
            return None, error_message

        mark.marks_obtained = marks_obtained
        db.session.commit()
        return mark, None

    @staticmethod
    def delete_manual_mark(manual_marks_id):
        """Delete a manual (experiment) mark."""
        mark = ManualMarks.query.get(manual_marks_id)
        if mark:
            db.session.delete(mark)
            db.session.commit()
            return True, None
        return False, "Manual mark not found."

    # -------------------- Practical Exam Marks --------------------
    @staticmethod
    def assign_practical_mark(student_id, subject_id, practical_exam_marks):
        """Assign practical exam marks with year verification."""
        is_valid, error_message = MarksModule._verify_year(student_id, subject_id)
        if not is_valid:
            return None, error_message

        new_mark = PracticalMarks(student_id=student_id, subject_id=subject_id,
                                  practical_exam_marks=practical_exam_marks)
        db.session.add(new_mark)
        db.session.commit()
        return new_mark, None

    @staticmethod
    def get_practical_marks(student_id, subject_id):
        """Fetch practical exam marks of a student."""
        return PracticalMarks.query.filter_by(student_id=student_id, subject_id=subject_id).first()

    @staticmethod
    def update_practical_mark(practical_marks_id, practical_exam_marks):
        """Update practical exam marks for a student with year verification."""
        mark = PracticalMarks.query.get(practical_marks_id)
        if not mark:
            return None, "Practical mark not found."

        is_valid, error_message = MarksModule._verify_year(mark.student_id, mark.subject_id)
        if not is_valid:
            return None, error_message

        mark.practical_exam_marks = practical_exam_marks
        db.session.commit()
        return mark, None

    @staticmethod
    def delete_practical_mark(practical_marks_id):
        """Delete practical exam marks."""
        mark = PracticalMarks.query.get(practical_marks_id)
        if mark:
            db.session.delete(mark)
            db.session.commit()
            return True, None
        return False, "Practical mark not found."

    # -------------------- Class Test Marks --------------------
    @staticmethod
    def assign_class_test_marks(student_id, subject_id, class_test_1, class_test_2):
        """Assign marks for Class Test 1 & 2 with year verification."""
        is_valid, error_message = MarksModule._verify_year(student_id, subject_id)
        if not is_valid:
            return None, error_message

        new_marks = ClassTestMarks(student_id=student_id, subject_id=subject_id,
                                   class_test_1=class_test_1, class_test_2=class_test_2)
        db.session.add(new_marks)
        db.session.commit()
        return new_marks, None

    @staticmethod
    def get_class_test_marks(student_id, subject_id):
        """Fetch class test marks of a student."""
        return ClassTestMarks.query.filter_by(student_id=student_id, subject_id=subject_id).first()

    @staticmethod
    def update_class_test_marks(class_test_marks_id, class_test_1, class_test_2):
        """Update class test marks for a student with year verification."""
        marks = ClassTestMarks.query.get(class_test_marks_id)
        if not marks:
            return None, "Class test marks not found."

        is_valid, error_message = MarksModule._verify_year(marks.student_id, marks.subject_id)
        if not is_valid:
            return None, error_message

        marks.class_test_1 = class_test_1
        marks.class_test_2 = class_test_2
        db.session.commit()
        return marks, None

    @staticmethod
    def delete_class_test_marks(class_test_marks_id):
        """Delete class test marks."""
        marks = ClassTestMarks.query.get(class_test_marks_id)
        if marks:
            db.session.delete(marks)
            db.session.commit()
            return True, None
        return False, "Class test marks not found."

    # -------------------- SLA Activity Marks --------------------
    @staticmethod
    def assign_sla_marks(student_id, subject_id, micro_project, assignment, other_marks):
        """Assign SLA marks (Micro Project, Assignment, Others) with year verification."""
        is_valid, error_message = MarksModule._verify_year(student_id, subject_id)
        if not is_valid:
            return None, error_message

        new_marks = SLAMarks(student_id=student_id, subject_id=subject_id,
                             micro_project=micro_project, assignment=assignment, other_marks=other_marks)
        db.session.add(new_marks)
        db.session.commit()
        return new_marks, None

    @staticmethod
    def get_sla_marks(student_id, subject_id):
        """Fetch SLA marks of a student."""
        return SLAMarks.query.filter_by(student_id=student_id, subject_id=subject_id).first()

    @staticmethod
    def update_sla_marks(sla_marks_id, micro_project, assignment, other_marks):
        """Update SLA marks for a student with year verification."""
        marks = SLAMarks.query.get(sla_marks_id)
        if not marks:
            return None, "SLA marks not found."

        is_valid, error_message = MarksModule._verify_year(marks.student_id, marks.subject_id)
        if not is_valid:
            return None, error_message
        marks.micro_project = micro_project
        marks.assignment = assignment
        marks.other_marks = other_marks
        db.session.commit()
        return marks, None

    @staticmethod
    def delete_sla_marks(sla_marks_id):
        """Delete SLA marks."""
        marks = SLAMarks.query.get(sla_marks_id)
        if marks:
            db.session.delete(marks)
            db.session.commit()
            return True, None
        return False, "SLA marks not found."