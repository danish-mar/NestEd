import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import statistics

class ReportingModule:
    """
    Enhanced reporting module for student academic performance.
    Generates professional reports in Excel and PDF formats with separate sections
    for different types of marks and proper formatting.
    """

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    REPORTS_DIR = os.path.join(BASE_DIR, "..", "reports")
    LOGO_PATH = os.path.join(BASE_DIR, "..", "static", "img", "logo.png")

    COLORS = {
        "header_bg": (41, 128, 185),  # Blue
        "header_text": (255, 255, 255),  # White
        "subheader_bg": (52, 152, 219),  # Light Blue
        "section_bg": (236, 240, 241),  # Light Gray
        "highlight": (46, 204, 113)  # Green
    }

    @staticmethod
    def generate_student_report(file_format="excel"):
        """Generate a comprehensive report for all students and their marks."""
        from app.models import Student, Subject, ManualMarks, PracticalMarks, ClassTestMarks, SLAMarks

        students = Student.query.all()

        if file_format == "excel":
            return ReportingModule._generate_excel_report(students)
        elif file_format == "pdf":
            return ReportingModule._generate_pdf_report(students)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    @staticmethod
    def generate_single_student_report(student_id, file_format="excel"):
        """Generate a detailed report for a specific student."""
        from app.models import Student, Subject, ManualMarks, PracticalMarks, ClassTestMarks, SLAMarks

        student = Student.query.get(student_id)
        if not student:
            return None  # Student not found

        if file_format == "excel":
            return ReportingModule._generate_excel_report([student], is_single_student=True)
        elif file_format == "pdf":
            return ReportingModule._generate_pdf_report([student], is_single_student=True)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    @staticmethod
    def _collect_student_data(students):
        """Collect all marks data for given students."""
        from app.models import Subject, ManualMarks, PracticalMarks, ClassTestMarks, SLAMarks

        all_data = {
            "student_info": [],
            "manual_marks": [],
            "practical_marks": [],
            "class_test_marks": [],
            "sla_marks": []
        }

        for idx, student in enumerate(students, start=1):
            student_info = {
                "sr_no": idx,
                "enrollment_number": student.enrollment_number,
                "exam_seat_number": student.exam_seat_number,
                "name": student.name,
                "student_id": student.student_id,
                "current_year": student.current_year
            }
            all_data["student_info"].append(student_info)

            subjects = Subject.query.filter_by(year=student.current_year).all()

            for subject in subjects:
                manual_marks = ManualMarks.query.filter_by(
                    student_id=student.student_id,
                    subject_id=subject.subject_id
                ).all()

                for mark in manual_marks:
                    mark_data = mark.serialize()
                    mark_data["student_name"] = student.name
                    mark_data["subject_id"] = subject.subject_id
                    all_data["manual_marks"].append(mark_data)

                practical_mark = PracticalMarks.query.filter_by(
                    student_id=student.student_id,
                    subject_id=subject.subject_id
                ).first()

                if practical_mark:
                    mark_data = {
                        "student_id": student.student_id,
                        "student_name": student.name,
                        "subject_id": subject.subject_id,
                        "practical_exam_marks": practical_mark.practical_exam_marks
                    }
                    all_data["practical_marks"].append(mark_data)

                class_test = ClassTestMarks.query.filter_by(
                    student_id=student.student_id,
                    subject_id=subject.subject_id
                ).first()

                if class_test:
                    mark_data = {
                        "student_id": student.student_id,
                        "student_name": student.name,
                        "subject_id": subject.subject_id,
                        "class_test_1": class_test.class_test_1,
                        "class_test_2": class_test.class_test_2,
                        "average": class_test.calculate_average()
                    }
                    all_data["class_test_marks"].append(mark_data)

                sla_mark = SLAMarks.query.filter_by(
                    student_id=student.student_id,
                    subject_id=subject.subject_id
                ).first()

                if sla_mark:
                    mark_data = {
                        "student_id": student.student_id,
                        "student_name": student.name,
                        "subject_id": subject.subject_id,
                        "micro_project": sla_mark.micro_project,
                        "assignment": sla_mark.assignment,
                        "other_marks": sla_mark.other_marks,
                        "total_sla": sla_mark.micro_project + sla_mark.assignment + sla_mark.other_marks
                    }
                    all_data["sla_marks"].append(mark_data)

        return all_data

    @staticmethod
    def _generate_excel_report(students, is_single_student=False):
        """Generate a comprehensive Excel report with multiple worksheets."""
        from app.models import Subject

        if is_single_student and students:
            filename = f"student_{students[0].student_id}_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
        else:
            filename = f"students_report_{datetime.now().strftime('%Y%m%d')}.xlsx"

        all_data = ReportingModule._collect_student_data(students)

        os.makedirs(ReportingModule.REPORTS_DIR, exist_ok=True)
        file_path = os.path.join(ReportingModule.REPORTS_DIR, filename)
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        workbook = writer.book

        header_format = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#2980b9', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        subheader_format = workbook.add_format({'bold': True, 'bg_color': '#3498db', 'border': 1, 'align': 'center'})
        cell_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
        highlight_format = workbook.add_format({'bold': True, 'bg_color': '#2ecc71', 'border': 1, 'align': 'center'})

        if all_data["manual_marks"]:
            worksheet = workbook.add_worksheet('Experiment Marks')
            worksheet.merge_range('A1:H1', 'EXPERIMENT MARKS', header_format)

            headers = ['Sr. No.', 'Enrollment No.', 'Exam Seat No.', 'Name']
            col = 0
            for header in headers:
                worksheet.write(1, col, header, subheader_format)
                col += 1

            max_experiments = max([len([m for m in all_data["manual_marks"] if m["student_id"] == s["student_id"]]) for s in all_data["student_info"]], default=0)
            for i in range(max_experiments):
                worksheet.write(1, col + i, f'Exp {i + 1}', subheader_format)
            worksheet.write(1, col + max_experiments, 'Total', highlight_format)

            row_num = 2
            for student in all_data["student_info"]:
                worksheet.write(row_num, 0, student["sr_no"], cell_format)
                worksheet.write(row_num, 1, student["enrollment_number"], cell_format)
                worksheet.write(row_num, 2, student["exam_seat_number"], cell_format)
                worksheet.write(row_num, 3, student["name"], cell_format)

                total = 0
                student_marks = [m for m in all_data["manual_marks"] if m["student_id"] == student["student_id"]]
                for i in range(max_experiments):
                    mark = next((m["marks_obtained"] for m in student_marks if m["experiment_number"] == i + 1), 0)
                    worksheet.write(row_num, 4 + i, mark, cell_format)
                    total += mark
                worksheet.write(row_num, 4 + max_experiments, total, highlight_format)
                row_num += 1

            worksheet.set_column(0, 0, 4)
            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 2, 15)
            worksheet.set_column(3, 3, 20)
            worksheet.set_column(4, 4 + max_experiments, 8)

        if all_data["practical_marks"]:
            worksheet = workbook.add_worksheet('Practical Marks')
            worksheet.merge_range('A1:E1', 'PRACTICAL EXAMINATION MARKS', header_format)

            headers = ['Sr. No.', 'Enrollment No.', 'Exam Seat No.', 'Name', 'Marks']
            for col, header in enumerate(headers):
                worksheet.write(1, col, header, subheader_format)

            row_num = 2
            for student in all_data["student_info"]:
                mark = next((m["practical_exam_marks"] for m in all_data["practical_marks"] if m["student_id"] == student["student_id"]), 0)
                worksheet.write(row_num, 0, student["sr_no"], cell_format)
                worksheet.write(row_num, 1, student["enrollment_number"], cell_format)
                worksheet.write(row_num, 2, student["exam_seat_number"], cell_format)
                worksheet.write(row_num, 3, student["name"], cell_format)
                worksheet.write(row_num, 4, mark, cell_format)
                row_num += 1

            worksheet.set_column(0, 0, 8)
            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 2, 15)
            worksheet.set_column(3, 3, 20)
            worksheet.set_column(4, 4, 10)

        if all_data["class_test_marks"]:
            worksheet = workbook.add_worksheet('Class Test Marks')
            worksheet.merge_range('A1:G1', 'CLASS TEST MARKS', header_format)

            headers = ['Sr. No.', 'Enrollment No.', 'Exam Seat No.', 'Name', 'Test 1', 'Test 2', 'Average']
            for col, header in enumerate(headers):
                worksheet.write(1, col, header, subheader_format)

            row_num = 2
            for student in all_data["student_info"]:
                mark = next((m for m in all_data["class_test_marks"] if m["student_id"] == student["student_id"]), None)
                worksheet.write(row_num, 0, student["sr_no"], cell_format)
                worksheet.write(row_num, 1, student["enrollment_number"], cell_format)
                worksheet.write(row_num, 2, student["exam_seat_number"], cell_format)
                worksheet.write(row_num, 3, student["name"], cell_format)
                worksheet.write(row_num, 4, mark["class_test_1"] if mark else 0, cell_format)
                worksheet.write(row_num, 5, mark["class_test_2"] if mark else 0, cell_format)
                worksheet.write(row_num, 6, mark["average"] if mark else 0, highlight_format)
                row_num += 1

            worksheet.set_column(0, 0, 8)
            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 2, 15)
            worksheet.set_column(3, 3, 20)
            worksheet.set_column(4, 6, 12)

        if all_data["sla_marks"]:
            worksheet = workbook.add_worksheet('SLA Marks')
            worksheet.merge_range('A1:H1', 'SLA ACTIVITY MARKS', header_format)

            headers = ['Sr. No.', 'Enrollment No.', 'Exam Seat No.', 'Name', 'Micro Project', 'Assignment', 'Other', 'Total']
            for col, header in enumerate(headers):
                worksheet.write(1, col, header, subheader_format)

            row_num = 2
            for student in all_data["student_info"]:
                mark = next((m for m in all_data["sla_marks"] if m["student_id"] == student["student_id"]), None)
                worksheet.write(row_num, 0, student["sr_no"], cell_format)
                worksheet.write(row_num, 1, student["enrollment_number"], cell_format)
                worksheet.write(row_num, 2, student["exam_seat_number"], cell_format)
                worksheet.write(row_num, 3, student["name"], cell_format)
                worksheet.write(row_num, 4, mark["micro_project"] if mark else 0, cell_format)
                worksheet.write(row_num, 5, mark["assignment"] if mark else 0, cell_format)
                worksheet.write(row_num, 6, mark["other_marks"] if mark else 0, cell_format)
                worksheet.write(row_num, 7, mark["total_sla"] if mark else 0, highlight_format)
                row_num += 1

            worksheet.set_column(0, 0, 8)
            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 2, 15)
            worksheet.set_column(3, 3, 20)
            worksheet.set_column(4, 7, 12)

        if is_single_student and students:
            student = students[0]
            subjects = Subject.query.filter_by(year=student.current_year).all()
            worksheet = workbook.add_worksheet('Consolidated Marks')
            worksheet.merge_range('A1:G1', 'CONSOLIDATED MARKS REPORT', header_format)

            headers = ['Sr. No.', 'Enrollment No.', 'Exam Seat No.', 'Name', 'Experiments', 'Practical', 'Class Test Avg', 'SLA', 'Total', 'Percentage']
            for col, header in enumerate(headers):
                worksheet.write(2, col, header, subheader_format)

            row_num = 3
            for idx, subject in enumerate(subjects, start=1):
                exp_total = sum(m["marks_obtained"] for m in all_data["manual_marks"] if m["subject_id"] == subject.subject_id)
                practical = next((m["practical_exam_marks"] for m in all_data["practical_marks"] if m["subject_id"] == subject.subject_id), 0)
                class_test = next((m["average"] for m in all_data["class_test_marks"] if m["subject_id"] == subject.subject_id), 0)
                sla = next((m["total_sla"] for m in all_data["sla_marks"] if m["subject_id"] == subject.subject_id), 0)
                total = exp_total + practical + class_test + sla
                percentage = (total / 400) * 100

                worksheet.write(row_num, 0, student["sr_no"], cell_format)
                worksheet.write(row_num, 1, student["enrollment_number"], cell_format)
                worksheet.write(row_num, 2, student["exam_seat_number"], cell_format)
                worksheet.write(row_num, 3, student["name"], cell_format)
                worksheet.write(row_num, 4, exp_total, cell_format)
                worksheet.write(row_num, 5, practical, cell_format)
                worksheet.write(row_num, 6, class_test, cell_format)
                worksheet.write(row_num, 7, sla, cell_format)
                worksheet.write(row_num, 8, total, cell_format)
                worksheet.write(row_num, 9, f"{percentage:.2f}%", highlight_format)
                row_num += 1

            worksheet.set_column(0, 0, 8)
            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 2, 15)
            worksheet.set_column(3, 3, 20)
            worksheet.set_column(4, 9, 12)

        writer.close()
        return file_path

    @staticmethod
    def _generate_pdf_report(students, is_single_student=False):
        """Generate a comprehensive PDF report with proper formatting."""
        from app.models import Subject

        if is_single_student and students:
            filename = f"student_{students[0].student_id}_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        else:
            filename = f"students_report_{datetime.now().strftime('%Y%m%d')}.pdf"

        all_data = ReportingModule._collect_student_data(students)

        class PDF(FPDF):
            def __init__(self):
                super().__init__(orientation='L')
                self.set_auto_page_break(auto=True, margin=15)

            def header(self):
                if os.path.exists(ReportingModule.LOGO_PATH):
                    self.image(ReportingModule.LOGO_PATH, 10, 8, 25)
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, 'ACADEMIC PERFORMANCE REPORT', 0, 1, 'C')
                self.set_font('Arial', 'I', 10)
                self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
                self.ln(5)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

            def section_title(self, title):
                self.set_font('Arial', 'B', 12)
                self.set_fill_color(*ReportingModule.COLORS["header_bg"])
                self.set_text_color(*ReportingModule.COLORS["header_text"])
                self.cell(0, 10, title, 1, 1, 'C', True)
                self.ln(2)

            def create_table(self, headers, data, col_widths, max_rows_per_page=20):
                self.set_font('Arial', 'B', 10)
                self.set_fill_color(*ReportingModule.COLORS["subheader_bg"])
                self.set_text_color(*ReportingModule.COLORS["header_text"])

                for i, header in enumerate(headers):
                    self.cell(col_widths[i], 10, str(header), 1, 0, 'C', True)
                self.ln()

                self.set_font('Arial', '', 9)
                self.set_text_color(0, 0, 0)

                row_count = 0
                for row in data:
                    if row_count >= max_rows_per_page:
                        self.add_page()
                        self.section_title(self.current_section)
                        self.create_table(headers, data[row_count:], col_widths, max_rows_per_page)
                        break
                    for i, value in enumerate(row):
                        self.cell(col_widths[i], 8, str(value), 1, 0, 'C')
                    self.ln()
                    row_count += 1

                self.ln(5)

        pdf = PDF()
        pdf.add_page()

        if all_data["manual_marks"]:
            pdf.section_title("EXPERIMENT MARKS")
            pdf.current_section = "EXPERIMENT MARKS"

            headers = ['Sr', 'Enrollment No', 'Exam Seat', 'Name']
            col_widths = [10, 20, 20, 30]
            max_experiments = max([len([m for m in all_data["manual_marks"] if m["student_id"] == s["student_id"]]) for s in all_data["student_info"]], default=0)

            for i in range(max_experiments):
                headers.append(f'E{i + 1}')
                col_widths.append(8)
            headers.append('Total')
            col_widths.append(25)

            data = []
            for student in all_data["student_info"]:
                row = [student["sr_no"], student["enrollment_number"], student["exam_seat_number"], student["name"]]
                total = 0
                student_marks = [m for m in all_data["manual_marks"] if m["student_id"] == student["student_id"]]
                for i in range(max_experiments):
                    mark = next((m["marks_obtained"] for m in student_marks if m["experiment_number"] == i + 1), 0)
                    row.append(mark)
                    total += mark
                row.append(total)
                data.append(row)

            pdf.create_table(headers, data, col_widths)

        if all_data["practical_marks"]:
            pdf.section_title("PRACTICAL EXAMINATION MARKS")
            pdf.current_section = "PRACTICAL EXAMINATION MARKS"

            headers = ['Sr. No.', 'Enrollment No.', 'Exam Seat No.', 'Name', 'Marks']
            col_widths = [20, 40, 40, 50, 40]
            data = [[s["sr_no"], s["enrollment_number"], s["exam_seat_number"], s["name"], next((m["practical_exam_marks"] for m in all_data["practical_marks"] if m["student_id"] == s["student_id"]), 0)] for s in all_data["student_info"]]

            pdf.create_table(headers, data, col_widths)

        if all_data["class_test_marks"]:
            pdf.section_title("CLASS TEST MARKS")
            pdf.current_section = "CLASS TEST MARKS"

            headers = ['Sr. No.', 'Enrollment No.', 'Exam Seat No.', 'Name', 'Test 1', 'Test 2', 'Average']
            col_widths = [20, 40, 40, 50, 30, 30, 30]
            data = [[s["sr_no"], s["enrollment_number"], s["exam_seat_number"], s["name"], m["class_test_1"] if m else 0, m["class_test_2"] if m else 0, m["average"] if m else 0] for s in all_data["student_info"] for m in [next((m for m in all_data["class_test_marks"] if m["student_id"] == s["student_id"]), None)]]

            pdf.create_table(headers, data, col_widths)

        if all_data["sla_marks"]:
            pdf.section_title("SLA ACTIVITY MARKS")
            pdf.current_section = "SLA ACTIVITY MARKS"

            headers = ['Sr. No.', 'Enrollment No.', 'Exam Seat No.', 'Name', 'Micro Project', 'Assignment', 'Other', 'Total']
            col_widths = [20, 40, 40, 50, 30, 30, 30, 30]
            data = [[s["sr_no"], s["enrollment_number"], s["exam_seat_number"], s["name"], m["micro_project"] if m else 0, m["assignment"] if m else 0, m["other_marks"] if m else 0, m["total_sla"] if m else 0] for s in all_data["student_info"] for m in [next((m for m in all_data["sla_marks"] if m["student_id"] == s["student_id"]), None)]]

            pdf.create_table(headers, data, col_widths)

        if is_single_student and students:
            student = students[0]
            subjects = Subject.query.filter_by(year=student.current_year).all()

            pdf.add_page()
            pdf.section_title(f"CONSOLIDATED MARKS - {student.name}")
            pdf.current_section = f"CONSOLIDATED MARKS - {student.name}"

            headers = ['Sr. No.', 'Enrollment No.', 'Exam Seat No.', 'Name', 'Experiments', 'Practical', 'Class Test Avg', 'SLA', 'Total', 'Percentage']
            col_widths = [20, 40, 40, 50, 30, 30, 30, 30, 30, 30]
            data = []

            for subject in subjects:
                exp_total = sum(m["marks_obtained"] for m in all_data["manual_marks"] if m["subject_id"] == subject.subject_id)
                practical = next((m["practical_exam_marks"] for m in all_data["practical_marks"] if m["subject_id"] == subject.subject_id), 0)
                class_test = next((m["average"] for m in all_data["class_test_marks"] if m["subject_id"] == subject.subject_id), 0)
                sla = next((m["total_sla"] for m in all_data["sla_marks"] if m["subject_id"] == subject.subject_id), 0)
                total = exp_total + practical + class_test + sla
                percentage = (total / 400) * 100

                data.append([student["sr_no"], student["enrollment_number"], student["exam_seat_number"], student["name"], exp_total, practical, f"{class_test:.2f}", sla, total, f"{percentage:.2f}%"])

            pdf.create_table(headers, data, col_widths)

            total_marks = sum(d[-2] for d in data)
            avg_percentage = (total_marks / (len(subjects) * 400)) * 100 if subjects else 0
            grade = "A+" if avg_percentage >= 90 else "A" if avg_percentage >= 80 else "B+" if avg_percentage >= 75 else "B" if avg_percentage >= 70 else "C+" if avg_percentage >= 65 else "C" if avg_percentage >= 60 else "D" if avg_percentage >= 50 else "F"

            pdf.add_page()
            pdf.section_title("PERFORMANCE SUMMARY")

            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"Student: {student.name} (ID: {student.student_id})", 0, 1)
            pdf.ln(5)

            pdf.set_fill_color(*ReportingModule.COLORS["section_bg"])
            pdf.rect(40, pdf.get_y(), 220, 60, 'F')
            y_pos = pdf.get_y() + 10
            pdf.set_xy(50, y_pos)
            pdf.cell(100, 10, "Overall Percentage:", 0, 0)
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(100, 10, f"{avg_percentage:.2f}%", 0, 1)
            pdf.set_font('Arial', 'B', 12)
            pdf.set_xy(50, y_pos + 15)
            pdf.cell(100, 10, "Total Marks Obtained:", 0, 0)
            pdf.set_font('Arial', '', 12)
            pdf.cell(100, 10, f"{total_marks} / {len(subjects) * 400}", 0, 1)
            pdf.set_xy(50, y_pos + 30)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(100, 10, "Grade:", 0, 0)
            pdf.set_font('Arial', '', 12)
            pdf.cell(100, 10, grade, 0, 1)

        os.makedirs(ReportingModule.REPORTS_DIR, exist_ok=True)
        file_path = os.path.join(ReportingModule.REPORTS_DIR, filename)
        pdf.output(file_path)
        return file_path

    @staticmethod
    def generate_subject_report(subject_id, file_format="excel"):
        """Generate a report for all students for a specific subject."""
        from app.models import Student, Subject, ManualMarks, PracticalMarks, ClassTestMarks, SLAMarks

        subject = Subject.query.get(subject_id)
        if not subject:
            return None

        students = Student.query.filter_by(current_year=subject.year).all()

        if file_format == "excel":
            return ReportingModule._generate_subject_excel_report(subject, students)
        elif file_format == "pdf":
            return ReportingModule._generate_subject_pdf_report(subject, students)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    @staticmethod
    def _generate_subject_excel_report(subject, students):
        """Generate an Excel report focused on a specific subject."""
        from app.models import ManualMarks, PracticalMarks, ClassTestMarks, SLAMarks

        filename = f"subject_{subject.subject_id}_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
        os.makedirs(ReportingModule.REPORTS_DIR, exist_ok=True)
        file_path = os.path.join(ReportingModule.REPORTS_DIR, filename)
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        workbook = writer.book

        header_format = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#2980b9', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        subheader_format = workbook.add_format({'bold': True, 'bg_color': '#3498db', 'border': 1, 'align': 'center'})
        cell_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
        highlight_format = workbook.add_format({'bold': True, 'bg_color': '#2ecc71', 'border': 1, 'align': 'center'})

        worksheet = workbook.add_worksheet('Overview')
        worksheet.merge_range('A1:I1', 'COMPREHENSIVE REPORT', header_format)

        headers = ['Sr. No.', 'Enrollment No.', 'Exam Seat No.', 'Name', 'Exp. Marks', 'Practical', 'Class Test Avg', 'SLA Total', 'Total Marks']
        for col, header in enumerate(headers):
            worksheet.write(1, col, header, subheader_format)

        row = 2
        all_data = ReportingModule._collect_student_data(students)
        for student in all_data["student_info"]:
            exp_total = sum(m["marks_obtained"] for m in all_data["manual_marks"] if m["student_id"] == student["student_id"] and m["subject_id"] == subject.subject_id)
            practical = next((m["practical_exam_marks"] for m in all_data["practical_marks"] if m["student_id"] == student["student_id"] and m["subject_id"] == subject.subject_id), 0)
            class_test = next((m["average"] for m in all_data["class_test_marks"] if m["student_id"] == student["student_id"] and m["subject_id"] == subject.subject_id), 0)
            sla = next((m["total_sla"] for m in all_data["sla_marks"] if m["student_id"] == student["student_id"] and m["subject_id"] == subject.subject_id), 0)
            total = exp_total + practical + class_test + sla

            worksheet.write(row, 0, student["sr_no"], cell_format)
            worksheet.write(row, 1, student["enrollment_number"], cell_format)
            worksheet.write(row, 2, student["exam_seat_number"], cell_format)
            worksheet.write(row, 3, student["name"], cell_format)
            worksheet.write(row, 4, exp_total, cell_format)
            worksheet.write(row, 5, practical, cell_format)
            worksheet.write(row, 6, class_test, cell_format)
            worksheet.write(row, 7, sla, cell_format)
            worksheet.write(row, 8, total, highlight_format)
            row += 1

        worksheet.set_column(0, 0, 8)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 15)
        worksheet.set_column(3, 3, 20)
        worksheet.set_column(4, 8, 12)

        writer.close()
        return file_path

    @staticmethod
    def _generate_subject_pdf_report(subject, students):
        """Generate a PDF report focused on a specific subject."""
        filename = f"subject_{subject.subject_id}_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        all_data = ReportingModule._collect_student_data(students)

        class PDF(FPDF):
            def __init__(self):
                super().__init__(orientation='L')
                self.set_auto_page_break(auto=True, margin=15)

            def header(self):
                if os.path.exists(ReportingModule.LOGO_PATH):
                    self.image(ReportingModule.LOGO_PATH, 10, 8, 25)
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, 'SUBJECT REPORT', 0, 1, 'C')
                self.set_font('Arial', 'I', 10)
                self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
                self.ln(5)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

            def section_title(self, title):
                self.set_font('Arial', 'B', 12)
                self.set_fill_color(*ReportingModule.COLORS["header_bg"])
                self.set_text_color(*ReportingModule.COLORS["header_text"])
                self.cell(0, 10, title, 1, 1, 'C', True)
                self.ln(2)

            def create_table(self, headers, data, col_widths, max_rows_per_page=20):
                self.set_font('Arial', 'B', 10)
                self.set_fill_color(*ReportingModule.COLORS["subheader_bg"])
                self.set_text_color(*ReportingModule.COLORS["header_text"])

                for i, header in enumerate(headers):
                    self.cell(col_widths[i], 10, str(header), 1, 0, 'C', True)
                self.ln()

                self.set_font('Arial', '', 9)
                self.set_text_color(0, 0, 0)

                row_count = 0
                for row in data:
                    if row_count >= max_rows_per_page:
                        self.add_page()
                        self.section_title(self.current_section)
                        self.create_table(headers, data[row_count:], col_widths, max_rows_per_page)
                        break
                    for i, value in enumerate(row):
                        self.cell(col_widths[i], 8, str(value), 1, 0, 'C')
                    self.ln()
                    row_count += 1

                self.ln(5)

        pdf = PDF()
        pdf.add_page()

        pdf.section_title(f"OVERVIEW - Year {subject.year}")
        pdf.current_section = f"OVERVIEW - Year {subject.year}"

        headers = ['Sr. No.', 'Enrollment No.', 'Exam Seat No.', 'Name', 'Exp. Marks', 'Practical', 'Class Test Avg', 'SLA Total', 'Total']
        col_widths = [20, 40, 40, 50, 30, 30, 30, 30, 30]
        data = [[s["sr_no"], s["enrollment_number"], s["exam_seat_number"], s["name"],
                 sum(m["marks_obtained"] for m in all_data["manual_marks"] if m["student_id"] == s["student_id"] and m["subject_id"] == subject.subject_id),
                 next((m["practical_exam_marks"] for m in all_data["practical_marks"] if m["student_id"] == s["student_id"] and m["subject_id"] == subject.subject_id), 0),
                 next((m["average"] for m in all_data["class_test_marks"] if m["student_id"] == s["student_id"] and m["subject_id"] == subject.subject_id), 0),
                 next((m["total_sla"] for m in all_data["sla_marks"] if m["student_id"] == s["student_id"] and m["subject_id"] == subject.subject_id), 0),
                 sum(m["marks_obtained"] for m in all_data["manual_marks"] if m["student_id"] == s["student_id"] and m["subject_id"] == subject.subject_id) +
                 next((m["practical_exam_marks"] for m in all_data["practical_marks"] if m["student_id"] == s["student_id"] and m["subject_id"] == subject.subject_id), 0) +
                 next((m["average"] for m in all_data["class_test_marks"] if m["student_id"] == s["student_id"] and m["subject_id"] == subject.subject_id), 0) +
                 next((m["total_sla"] for m in all_data["sla_marks"] if m["student_id"] == s["student_id"] and m["subject_id"] == subject.subject_id), 0)]
                for s in all_data["student_info"]]

        pdf.create_table(headers, data, col_widths)

        os.makedirs(ReportingModule.REPORTS_DIR, exist_ok=True)
        file_path = os.path.join(ReportingModule.REPORTS_DIR, filename)
        pdf.output(file_path)
        return file_path