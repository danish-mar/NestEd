import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime


class ReportingModule:
    """
    Enhanced reporting module for student academic performance.
    Generates professional reports in Excel and PDF formats with separate sections
    for different types of marks and proper formatting.
    """

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    REPORTS_DIR = os.path.join(BASE_DIR, "..", "reports")
    LOGO_PATH = os.path.join(BASE_DIR, "..", "static", "img", "logo.png")

    # Define colors for reports
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

        for student in students:
            # Basic student info
            student_info = student.serialize()
            all_data["student_info"].append(student_info)

            # Get all subjects for this student's current year
            subjects = Subject.query.filter_by(year=student.current_year).all()

            for subject in subjects:
                # Manual (Experiment) marks
                manual_marks = ManualMarks.query.filter_by(
                    student_id=student.student_id,
                    subject_id=subject.subject_id
                ).all()

                for mark in manual_marks:
                    mark_data = mark.serialize()
                    mark_data["student_name"] = student.name
                    mark_data["subject_name"] = subject.subject_name
                    all_data["manual_marks"].append(mark_data)

                # Practical marks
                practical_mark = PracticalMarks.query.filter_by(
                    student_id=student.student_id,
                    subject_id=subject.subject_id
                ).first()

                if practical_mark:
                    mark_data = {
                        "student_id": student.student_id,
                        "student_name": student.name,
                        "subject_id": subject.subject_id,
                        "subject_name": subject.subject_name,
                        "practical_exam_marks": practical_mark.practical_exam_marks
                    }
                    all_data["practical_marks"].append(mark_data)

                # Class test marks
                class_test = ClassTestMarks.query.filter_by(
                    student_id=student.student_id,
                    subject_id=subject.subject_id
                ).first()

                if class_test:
                    mark_data = {
                        "student_id": student.student_id,
                        "student_name": student.name,
                        "subject_id": subject.subject_id,
                        "subject_name": subject.subject_name,
                        "class_test_1": class_test.class_test_1,
                        "class_test_2": class_test.class_test_2,
                        "average": class_test.calculate_average()
                    }
                    all_data["class_test_marks"].append(mark_data)

                # SLA marks
                sla_mark = SLAMarks.query.filter_by(
                    student_id=student.student_id,
                    subject_id=subject.subject_id
                ).first()

                if sla_mark:
                    mark_data = {
                        "student_id": student.student_id,
                        "student_name": student.name,
                        "subject_id": subject.subject_id,
                        "subject_name": subject.subject_name,
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

        # Create a filename based on whether it's for a single student or multiple
        if is_single_student and students:
            filename = f"student_{students[0].student_id}_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
        else:
            filename = f"students_report_{datetime.now().strftime('%Y%m%d')}.xlsx"

        # Collect all data
        all_data = ReportingModule._collect_student_data(students)

        # Create a Pandas Excel writer using XlsxWriter as the engine
        os.makedirs(ReportingModule.REPORTS_DIR, exist_ok=True)
        file_path = os.path.join(ReportingModule.REPORTS_DIR, filename)
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        workbook = writer.book

        # Create formats
        header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#2980b9',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        subheader_format = workbook.add_format({
            'bold': True,
            'bg_color': '#3498db',
            'border': 1,
            'align': 'center'
        })

        cell_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        highlight_format = workbook.add_format({
            'bold': True,
            'bg_color': '#2ecc71',
            'border': 1,
            'align': 'center'
        })

        # ----- Student Information Sheet -----
        if all_data["student_info"]:
            df_students = pd.DataFrame(all_data["student_info"])
            worksheet = workbook.add_worksheet('Student Information')

            # Write title
            worksheet.merge_range('A1:K1', 'STUDENT INFORMATION', header_format)

            # Write data
            columns = ['Student ID', 'Name', 'Email', 'Phone', 'DOB', 'Gender',
                       'Address', 'Current Year', 'Admission Year', 'Enrollment Number', 'Exam Seat Number']

            for col_num, column in enumerate(columns):
                worksheet.write(1, col_num, column, subheader_format)

            for row_num, student in enumerate(all_data["student_info"]):
                worksheet.write(row_num + 2, 0, student['student_id'], cell_format)
                worksheet.write(row_num + 2, 1, student['name'], cell_format)
                worksheet.write(row_num + 2, 2, student['email'], cell_format)
                worksheet.write(row_num + 2, 3, student['phone'], cell_format)
                worksheet.write(row_num + 2, 4, student['dob'], cell_format)
                worksheet.write(row_num + 2, 5, student['gender'], cell_format)
                worksheet.write(row_num + 2, 6, student['address'], cell_format)
                worksheet.write(row_num + 2, 7, student['current_year'], cell_format)
                worksheet.write(row_num + 2, 8, student['admission_year'], cell_format)
                worksheet.write(row_num + 2, 9, student['enrollment_number'], cell_format)
                worksheet.write(row_num + 2, 10, student['exam_seat_number'], cell_format)

            # Adjust column widths
            for col_num in range(len(columns)):
                worksheet.set_column(col_num, col_num, 15)

        # ----- Manual Marks (Experiments) Sheet -----
        if all_data["manual_marks"]:
            # Group by student and subject
            students_subjects = {}
            for mark in all_data["manual_marks"]:
                key = (mark["student_id"], mark["subject_id"])
                if key not in students_subjects:
                    students_subjects[key] = {
                        "student_id": mark["student_id"],
                        "student_name": mark["student_name"],
                        "subject_id": mark["subject_id"],
                        "subject_name": mark["subject_name"],
                        "experiments": {}
                    }
                students_subjects[key]["experiments"][mark["experiment_number"]] = mark["marks_obtained"]

            # Create worksheet
            worksheet = workbook.add_worksheet('Experiment Marks')

            # Write title
            worksheet.merge_range('A1:I1', 'EXPERIMENT MARKS', header_format)

            # Write headers
            worksheet.write(1, 0, 'Student ID', subheader_format)
            worksheet.write(1, 1, 'Student Name', subheader_format)
            worksheet.write(1, 2, 'Subject', subheader_format)
            for i in range(5):
                worksheet.write(1, 3 + i, f'Exp {i + 1}', subheader_format)
            worksheet.write(1, 8, 'Total', highlight_format)

            # Write data
            row_num = 2
            for key, data in students_subjects.items():
                worksheet.write(row_num, 0, data["student_id"], cell_format)
                worksheet.write(row_num, 1, data["student_name"], cell_format)
                worksheet.write(row_num, 2, data["subject_name"], cell_format)

                total = 0
                for i in range(5):  # Assuming 5 experiments per sheet
                    mark = data["experiments"].get(i + 1, 0)
                    worksheet.write(row_num, 3 + i, mark, cell_format)
                    total += mark

                worksheet.write(row_num, 8, total, highlight_format)
                row_num += 1

            # Adjust column widths
            worksheet.set_column(0, 0, 10)
            worksheet.set_column(1, 1, 20)
            worksheet.set_column(2, 2, 15)
            worksheet.set_column(3, 8, 10)

        # ----- Practical Marks Sheet -----
        if all_data["practical_marks"]:
            df_practical = pd.DataFrame(all_data["practical_marks"])
            worksheet = workbook.add_worksheet('Practical Marks')

            # Write title
            worksheet.merge_range('A1:D1', 'PRACTICAL EXAMINATION MARKS', header_format)

            # Write headers
            worksheet.write(1, 0, 'Student ID', subheader_format)
            worksheet.write(1, 1, 'Student Name', subheader_format)
            worksheet.write(1, 2, 'Subject', subheader_format)
            worksheet.write(1, 3, 'Practical Marks', subheader_format)

            # Write data
            for row_num, mark in enumerate(all_data["practical_marks"]):
                worksheet.write(row_num + 2, 0, mark['student_id'], cell_format)
                worksheet.write(row_num + 2, 1, mark['student_name'], cell_format)
                worksheet.write(row_num + 2, 2, mark['subject_name'], cell_format)
                worksheet.write(row_num + 2, 3, mark['practical_exam_marks'], cell_format)

            # Adjust column widths
            worksheet.set_column(0, 0, 10)
            worksheet.set_column(1, 1, 20)
            worksheet.set_column(2, 2, 15)
            worksheet.set_column(3, 3, 15)

        # ----- Class Test Marks Sheet -----
        if all_data["class_test_marks"]:
            df_class_test = pd.DataFrame(all_data["class_test_marks"])
            worksheet = workbook.add_worksheet('Class Test Marks')

            # Write title
            worksheet.merge_range('A1:F1', 'CLASS TEST MARKS', header_format)

            # Write headers
            worksheet.write(1, 0, 'Student ID', subheader_format)
            worksheet.write(1, 1, 'Student Name', subheader_format)
            worksheet.write(1, 2, 'Subject', subheader_format)
            worksheet.write(1, 3, 'Class Test 1', subheader_format)
            worksheet.write(1, 4, 'Class Test 2', subheader_format)
            worksheet.write(1, 5, 'Average', highlight_format)

            # Write data
            for row_num, mark in enumerate(all_data["class_test_marks"]):
                worksheet.write(row_num + 2, 0, mark['student_id'], cell_format)
                worksheet.write(row_num + 2, 1, mark['student_name'], cell_format)
                worksheet.write(row_num + 2, 2, mark['subject_name'], cell_format)
                worksheet.write(row_num + 2, 3, mark['class_test_1'], cell_format)
                worksheet.write(row_num + 2, 4, mark['class_test_2'], cell_format)
                worksheet.write(row_num + 2, 5, mark['average'], highlight_format)

            # Adjust column widths
            worksheet.set_column(0, 0, 10)
            worksheet.set_column(1, 1, 20)
            worksheet.set_column(2, 2, 15)
            worksheet.set_column(3, 5, 12)

        # ----- SLA Marks Sheet -----
        if all_data["sla_marks"]:
            df_sla = pd.DataFrame(all_data["sla_marks"])
            worksheet = workbook.add_worksheet('SLA Marks')

            # Write title
            worksheet.merge_range('A1:G1', 'SLA ACTIVITY MARKS', header_format)

            # Write headers
            worksheet.write(1, 0, 'Student ID', subheader_format)
            worksheet.write(1, 1, 'Student Name', subheader_format)
            worksheet.write(1, 2, 'Subject', subheader_format)
            worksheet.write(1, 3, 'Micro Project', subheader_format)
            worksheet.write(1, 4, 'Assignment', subheader_format)
            worksheet.write(1, 5, 'Other Marks', subheader_format)
            worksheet.write(1, 6, 'Total SLA', highlight_format)

            # Write data
            for row_num, mark in enumerate(all_data["sla_marks"]):
                worksheet.write(row_num + 2, 0, mark['student_id'], cell_format)
                worksheet.write(row_num + 2, 1, mark['student_name'], cell_format)
                worksheet.write(row_num + 2, 2, mark['subject_name'], cell_format)
                worksheet.write(row_num + 2, 3, mark['micro_project'], cell_format)
                worksheet.write(row_num + 2, 4, mark['assignment'], cell_format)
                worksheet.write(row_num + 2, 5, mark['other_marks'], cell_format)
                worksheet.write(row_num + 2, 6, mark['total_sla'], highlight_format)

            # Adjust column widths
            worksheet.set_column(0, 0, 10)
            worksheet.set_column(1, 1, 20)
            worksheet.set_column(2, 2, 15)
            worksheet.set_column(3, 6, 12)

        # ----- Consolidated Marks Sheet -----
        if is_single_student and students:
            student = students[0]
            subjects = Subject.query.filter_by(year=student.current_year).all()

            worksheet = workbook.add_worksheet('Consolidated Marks')

            # Write title
            worksheet.merge_range('A1:G1', 'CONSOLIDATED MARKS REPORT', header_format)

            # Write student info
            worksheet.merge_range('A2:G2', f'Student: {student.name} (ID: {student.student_id})', subheader_format)
            worksheet.merge_range('A3:G3', f'Year: {student.current_year} | Enrollment: {student.enrollment_number}',
                                  subheader_format)

            # Write headers
            row_num = 4
            worksheet.write(row_num, 0, 'Subject', subheader_format)
            worksheet.write(row_num, 1, 'Experiment Marks', subheader_format)
            worksheet.write(row_num, 2, 'Practical Exam', subheader_format)
            worksheet.write(row_num, 3, 'Class Test Avg', subheader_format)
            worksheet.write(row_num, 4, 'SLA Total', subheader_format)
            worksheet.write(row_num, 5, 'Total Marks', subheader_format)
            worksheet.write(row_num, 6, 'Percentage', highlight_format)

            # Write data
            row_num = 5
            for subject in subjects:
                worksheet.write(row_num, 0, subject.subject_name, cell_format)

                # Calculate experiment marks total
                exp_total = 0
                manual_marks = [m for m in all_data["manual_marks"] if
                                m["student_id"] == student.student_id and m["subject_id"] == subject.subject_id]
                for mark in manual_marks:
                    exp_total += mark["marks_obtained"]
                worksheet.write(row_num, 1, exp_total, cell_format)

                # Get practical exam marks
                practical_mark = next((m for m in all_data["practical_marks"] if
                                       m["student_id"] == student.student_id and m["subject_id"] == subject.subject_id),
                                      None)
                practical_value = practical_mark["practical_exam_marks"] if practical_mark else 0
                worksheet.write(row_num, 2, practical_value, cell_format)

                # Get class test average
                class_test = next((m for m in all_data["class_test_marks"] if
                                   m["student_id"] == student.student_id and m["subject_id"] == subject.subject_id),
                                  None)
                class_test_avg = class_test["average"] if class_test else 0
                worksheet.write(row_num, 3, class_test_avg, cell_format)

                # Get SLA total
                sla_mark = next((m for m in all_data["sla_marks"] if
                                 m["student_id"] == student.student_id and m["subject_id"] == subject.subject_id), None)
                sla_total = sla_mark["total_sla"] if sla_mark else 0
                worksheet.write(row_num, 4, sla_total, cell_format)

                # Calculate total marks - assuming each category has equal weight
                total_marks = exp_total + practical_value + class_test_avg + sla_total
                worksheet.write(row_num, 5, total_marks, cell_format)

                # Calculate percentage (assuming max marks is 400 - 100 for each category)
                percentage = (total_marks / 400) * 100
                worksheet.write(row_num, 6, f"{percentage:.2f}%", highlight_format)

                row_num += 1

            # Adjust column widths
            worksheet.set_column(0, 0, 20)
            worksheet.set_column(1, 6, 15)

        # Save the workbook
        writer.close()

        return file_path

    @staticmethod
    def _generate_pdf_report(students, is_single_student=False):
        """Generate a comprehensive PDF report with proper formatting."""
        from app.models import Subject

        # Create a filename based on whether it's for a single student or multiple
        if is_single_student and students:
            filename = f"student_{students[0].student_id}_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        else:
            filename = f"students_report_{datetime.now().strftime('%Y%m%d')}.pdf"

        # Collect all data
        all_data = ReportingModule._collect_student_data(students)

        # Create PDF
        class PDF(FPDF):
            def __init__(self):
                super().__init__(orientation='L')  # Landscape orientation
                self.set_auto_page_break(auto=True, margin=15)

            def header(self):
                # Add logo if it exists
                if os.path.exists(ReportingModule.LOGO_PATH):
                    self.image(ReportingModule.LOGO_PATH, 10, 8, 25)
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, 'STUDENT ACADEMIC PERFORMANCE REPORT', 0, 1, 'C')
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

            def create_table(self, headers, data, col_widths):
                # Headers
                self.set_font('Arial', 'B', 10)
                self.set_fill_color(*ReportingModule.COLORS["subheader_bg"])
                self.set_text_color(*ReportingModule.COLORS["header_text"])

                for i, header in enumerate(headers):
                    self.cell(col_widths[i], 10, str(header), 1, 0, 'C', True)
                self.ln()

                # Data
                self.set_font('Arial', '', 9)
                self.set_text_color(0, 0, 0)

                for row in data:
                    for i, value in enumerate(row):
                        self.cell(col_widths[i], 8, str(value), 1, 0, 'C')
                    self.ln()

                self.ln(5)

        # Create PDF instance
        pdf = PDF()
        pdf.add_page()

        # ----- Student Information Section -----
        if all_data["student_info"]:
            pdf.section_title("STUDENT INFORMATION")

            # Create table
            headers = ['ID', 'Name', 'Email', 'Phone', 'Year', 'Enrollment No.']
            col_widths = [20, 40, 60, 30, 20, 50]

            data = []
            for student in all_data["student_info"]:
                data.append([
                    student['student_id'],
                    student['name'],
                    student['email'],
                    student['phone'],
                    student['current_year'],
                    student['enrollment_number']
                ])

            pdf.create_table(headers, data, col_widths)

        # ----- Consolidated Marks Section (for single student) -----
        if is_single_student and students:
            student = students[0]
            subjects = Subject.query.filter_by(year=student.current_year).all()

            pdf.section_title(f"CONSOLIDATED MARKS - {student.name}")

            # Create table
            headers = ['Subject', 'Experiments', 'Practical', 'Class Tests', 'SLA', 'Total', 'Percentage']
            col_widths = [50, 30, 30, 30, 30, 30, 30]

            data = []
            for subject in subjects:
                # Calculate experiment marks total
                exp_total = 0
                manual_marks = [m for m in all_data["manual_marks"] if
                                m["student_id"] == student.student_id and m["subject_id"] == subject.subject_id]
                for mark in manual_marks:
                    exp_total += mark["marks_obtained"]

                # Get practical exam marks
                practical_mark = next((m for m in all_data["practical_marks"] if
                                       m["student_id"] == student.student_id and m["subject_id"] == subject.subject_id),
                                      None)
                practical_value = practical_mark["practical_exam_marks"] if practical_mark else 0

                # Get class test average
                class_test = next((m for m in all_data["class_test_marks"] if
                                   m["student_id"] == student.student_id and m["subject_id"] == subject.subject_id),
                                  None)
                class_test_avg = class_test["average"] if class_test else 0

                # Get SLA total
                sla_mark = next((m for m in all_data["sla_marks"] if
                                 m["student_id"] == student.student_id and m["subject_id"] == subject.subject_id), None)
                sla_total = sla_mark["total_sla"] if sla_mark else 0

                # Calculate total marks
                total_marks = exp_total + practical_value + class_test_avg + sla_total

                # Calculate percentage (assuming max marks is 400 - 100 for each category)
                percentage = (total_marks / 400) * 100

                data.append([
                    subject.subject_name,
                    f"{exp_total}",
                    f"{practical_value}",
                    f"{class_test_avg:.2f}",
                    f"{sla_total}",
                    f"{total_marks}",
                    f"{percentage:.2f}%"
                ])

            pdf.create_table(headers, data, col_widths)

        # ----- Experiment Marks Section -----
        if all_data["manual_marks"]:
            pdf.section_title("EXPERIMENT MARKS")

            # Group by student and subject
            students_subjects = {}
            for mark in all_data["manual_marks"]:
                key = (mark["student_id"], mark["subject_id"])
                if key not in students_subjects:
                    students_subjects[key] = {
                        "student_id": mark["student_id"],
                        "student_name": mark["student_name"],
                        "subject_id": mark["subject_id"],
                        "subject_name": mark["subject_name"],
                        "experiments": {}
                    }
                students_subjects[key]["experiments"][mark["experiment_number"]] = mark["marks_obtained"]

            # Create table
            headers = ['Student ID', 'Name', 'Subject', 'Exp 1', 'Exp 2', 'Exp 3', 'Exp 4', 'Exp 5', 'Total']
            col_widths = [25, 40, 50, 20, 20, 20, 20, 20, 25]

            data = []
            for key, data_item in students_subjects.items():
                row = [
                    data_item["student_id"],
                    data_item["student_name"],
                    data_item["subject_name"]
                ]

                total = 0
                for i in range(5):  # Assuming 5 experiments
                    mark = data_item["experiments"].get(i + 1, 0)
                    row.append(mark)
                    total += mark

                row.append(total)
                data.append(row)

            pdf.create_table(headers, data, col_widths)

        # ----- Practical Marks Section -----
        if all_data["practical_marks"]:
            pdf.section_title("PRACTICAL EXAMINATION MARKS")

            # Create table
            headers = ['Student ID', 'Name', 'Subject', 'Practical Marks']
            col_widths = [30, 60, 90, 40]

            data = []
            for mark in all_data["practical_marks"]:
                data.append([
                    mark['student_id'],
                    mark['student_name'],
                    mark['subject_name'],
                    mark['practical_exam_marks']
                ])

            pdf.create_table(headers, data, col_widths)

        # ----- Class Test Marks Section -----
        if all_data["class_test_marks"]:
            pdf.section_title("CLASS TEST MARKS")

            # Create table
            # Create table
            headers = ['Student ID', 'Name', 'Subject', 'Class Test 1', 'Class Test 2', 'Average']
            col_widths = [30, 60, 60, 35, 35, 35]

            data = []
            for mark in all_data["class_test_marks"]:
                data.append([
                    mark['student_id'],
                    mark['student_name'],
                    mark['subject_name'],
                    mark['class_test_1'],
                    mark['class_test_2'],
                    f"{mark['average']:.2f}"
                ])

            pdf.create_table(headers, data, col_widths)

        # ----- SLA Marks Section -----
        if all_data["sla_marks"]:
            pdf.section_title("SLA ACTIVITY MARKS")

            # Create table
            headers = ['Student ID', 'Name', 'Subject', 'Micro Project', 'Assignment', 'Other', 'Total']
            col_widths = [25, 50, 55, 35, 35, 25, 25]

            data = []
            for mark in all_data["sla_marks"]:
                data.append([
                    mark['student_id'],
                    mark['student_name'],
                    mark['subject_name'],
                    mark['micro_project'],
                    mark['assignment'],
                    mark['other_marks'],
                    mark['total_sla']
                ])

            pdf.create_table(headers, data, col_widths)

        # ----- Performance Summary (for single student) -----
        if is_single_student and students:
            student = students[0]

            # Calculate overall performance metrics
            total_subjects = len(Subject.query.filter_by(year=student.current_year).all())
            if total_subjects > 0:
                # Calculate average marks across all subjects
                total_marks = 0
                total_percentage = 0

                subjects = Subject.query.filter_by(year=student.current_year).all()
                for subject in subjects:
                    # Calculate experiment marks total
                    exp_total = 0
                    manual_marks = [m for m in all_data["manual_marks"] if
                                    m["student_id"] == student.student_id and m["subject_id"] == subject.subject_id]
                    for mark in manual_marks:
                        exp_total += mark["marks_obtained"]

                    # Get practical exam marks
                    practical_mark = next((m for m in all_data["practical_marks"] if
                                           m["student_id"] == student.student_id and m[
                                               "subject_id"] == subject.subject_id), None)
                    practical_value = practical_mark["practical_exam_marks"] if practical_mark else 0

                    # Get class test average
                    class_test = next((m for m in all_data["class_test_marks"] if
                                       m["student_id"] == student.student_id and m["subject_id"] == subject.subject_id),
                                      None)
                    class_test_avg = class_test["average"] if class_test else 0

                    # Get SLA total
                    sla_mark = next((m for m in all_data["sla_marks"] if
                                     m["student_id"] == student.student_id and m["subject_id"] == subject.subject_id),
                                    None)
                    sla_total = sla_mark["total_sla"] if sla_mark else 0

                    # Calculate subject total marks
                    subject_total = exp_total + practical_value + class_test_avg + sla_total
                    total_marks += subject_total

                    # Calculate percentage
                    subject_percentage = (subject_total / 400) * 100  # Assuming 400 max marks per subject
                    total_percentage += subject_percentage

                avg_percentage = total_percentage / total_subjects

                # Add performance summary section
                pdf.add_page()
                pdf.section_title("PERFORMANCE SUMMARY")

                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f"Student: {student.name} (ID: {student.student_id})", 0, 1)
                pdf.cell(0, 10, f"Year: {student.current_year} | Enrollment No: {student.enrollment_number}", 0, 1)
                pdf.ln(5)

                # Create a summary box
                pdf.set_fill_color(*ReportingModule.COLORS["section_bg"])
                pdf.rect(40, pdf.get_y(), 220, 60, 'F')

                pdf.set_font('Arial', 'B', 12)
                y_pos = pdf.get_y() + 10
                pdf.set_xy(50, y_pos)
                pdf.cell(100, 10, "Overall Percentage:", 0, 0)
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(100, 10, f"{avg_percentage:.2f}%", 0, 1)

                pdf.set_font('Arial', 'B', 12)
                pdf.set_xy(50, y_pos + 15)
                pdf.cell(100, 10, "Total Marks Obtained:", 0, 0)
                pdf.set_font('Arial', '', 12)
                pdf.cell(100, 10, f"{total_marks} / {total_subjects * 400}", 0, 1)

                pdf.set_font('Arial', 'B', 12)
                pdf.set_xy(50, y_pos + 30)
                pdf.cell(100, 10, "Subjects:", 0, 0)
                pdf.set_font('Arial', '', 12)
                pdf.cell(100, 10, f"{total_subjects}", 0, 1)

                # Add a grade based on percentage
                grade = "A+"
                if avg_percentage < 90:
                    grade = "A"
                if avg_percentage < 80:
                    grade = "B+"
                if avg_percentage < 70:
                    grade = "B"
                if avg_percentage < 60:
                    grade = "C"
                if avg_percentage < 50:
                    grade = "D"
                if avg_percentage < 40:
                    grade = "F"

                pdf.ln(15)
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, f"Overall Grade: {grade}", 0, 1, 'C')

                # Add comments section
                pdf.ln(10)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, "Comments:", 0, 1)

                pdf.set_fill_color(255, 255, 255)
                pdf.rect(40, pdf.get_y(), 220, 40, 'FD')

                # Add default comment based on performance
                comment = ""
                if avg_percentage >= 80:
                    comment = "Excellent performance across all subjects! Keep up the good work."
                elif avg_percentage >= 70:
                    comment = "Very good performance. Continue working hard to excel further."
                elif avg_percentage >= 60:
                    comment = "Good performance. Focus on improving weaker areas to achieve better results."
                elif avg_percentage >= 50:
                    comment = "Satisfactory performance. More consistent study habits recommended."
                else:
                    comment = "Needs improvement. Regular attendance and additional effort required."

                pdf.set_font('Arial', '', 10)
                pdf.set_xy(45, pdf.get_y() + 5)
                pdf.multi_cell(210, 10, comment, 0, 'L')

                # Add signature section
                pdf.ln(50)
                pdf.line(50, pdf.get_y(), 120, pdf.get_y())  # Signature line
                pdf.line(180, pdf.get_y(), 250, pdf.get_y())  # Signature line

                pdf.set_font('Arial', '', 10)
                pdf.set_xy(60, pdf.get_y() + 5)
                pdf.cell(50, 10, "Class Teacher", 0, 0, 'C')

                pdf.set_xy(200, pdf.get_y())
                pdf.cell(50, 10, "HOD", 0, 1, 'C')

        # Save PDF
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
            return None  # Subject not found

        # Get all students in the year of this subject
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

        # Create filename
        filename = f"subject_{subject.subject_id}_{subject.subject_name}_report_{datetime.now().strftime('%Y%m%d')}.xlsx"

        # Create Excel writer
        os.makedirs(ReportingModule.REPORTS_DIR, exist_ok=True)
        file_path = os.path.join(ReportingModule.REPORTS_DIR, filename)
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        workbook = writer.book

        # Create formats
        header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#2980b9',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        subheader_format = workbook.add_format({
            'bold': True,
            'bg_color': '#3498db',
            'border': 1,
            'align': 'center'
        })

        cell_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        highlight_format = workbook.add_format({
            'bold': True,
            'bg_color': '#2ecc71',
            'border': 1,
            'align': 'center'
        })

        # Create main worksheet
        worksheet = workbook.add_worksheet(f"{subject.subject_name} Overview")

        # Write title
        worksheet.merge_range('A1:H1', f"{subject.subject_name.upper()} - COMPREHENSIVE REPORT", header_format)
        worksheet.merge_range('A2:H2', f"Year: {subject.year}", subheader_format)

        # Write headers
        row = 3
        worksheet.write(row, 0, "Student ID", subheader_format)
        worksheet.write(row, 1, "Student Name", subheader_format)
        worksheet.write(row, 2, "Experiment Marks", subheader_format)
        worksheet.write(row, 3, "Practical Exam", subheader_format)
        worksheet.write(row, 4, "Class Test 1", subheader_format)
        worksheet.write(row, 5, "Class Test 2", subheader_format)
        worksheet.write(row, 6, "SLA Total", subheader_format)
        worksheet.write(row, 7, "Total Marks", highlight_format)

        row += 1

        # Write data for each student
        for student in students:
            # Get experiment marks
            manual_marks = ManualMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).all()

            exp_total = sum(mark.marks_obtained for mark in manual_marks)

            # Get practical exam marks
            practical_mark = PracticalMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).first()

            practical_value = practical_mark.practical_exam_marks if practical_mark else 0

            # Get class test marks
            class_test = ClassTestMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).first()

            ct1 = class_test.class_test_1 if class_test else 0
            ct2 = class_test.class_test_2 if class_test else 0

            # Get SLA marks
            sla_mark = SLAMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).first()

            sla_total = 0
            if sla_mark:
                sla_total = sla_mark.micro_project + sla_mark.assignment + sla_mark.other_marks

            # Calculate total
            total_marks = exp_total + practical_value + (ct1 + ct2) / 2 + sla_total

            # Write row
            worksheet.write(row, 0, student.student_id, cell_format)
            worksheet.write(row, 1, student.name, cell_format)
            worksheet.write(row, 2, exp_total, cell_format)
            worksheet.write(row, 3, practical_value, cell_format)
            worksheet.write(row, 4, ct1, cell_format)
            worksheet.write(row, 5, ct2, cell_format)
            worksheet.write(row, 6, sla_total, cell_format)
            worksheet.write(row, 7, total_marks, highlight_format)

            row += 1

        # Adjust column widths
        worksheet.set_column(0, 0, 12)
        worksheet.set_column(1, 1, 25)
        worksheet.set_column(2, 7, 15)

        # Add detailed experiment marks worksheet
        exp_worksheet = workbook.add_worksheet("Experiment Marks")

        # Write headers
        row = 0
        exp_worksheet.merge_range(row, 0, row, 31, f"{subject.subject_name.upper()} - EXPERIMENT MARKS", header_format)
        row += 1

        exp_worksheet.write(row, 0, "Student ID", subheader_format)
        exp_worksheet.write(row, 1, "Student Name", subheader_format)

        for i in range(30):  # Assuming maximum 30 experiments
            exp_worksheet.write(row, i + 2, f"Exp {i + 1}", subheader_format)

        row += 1

        # Write data for each student
        for student in students:
            exp_worksheet.write(row, 0, student.student_id, cell_format)
            exp_worksheet.write(row, 1, student.name, cell_format)

            # Get all experiments for this student
            manual_marks = ManualMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).all()

            # Create a dictionary for easy lookup
            exp_dict = {mark.experiment_number: mark.marks_obtained for mark in manual_marks}

            # Fill in experiment marks
            for i in range(30):
                mark = exp_dict.get(i + 1, 0)
                exp_worksheet.write(row, i + 2, mark, cell_format)

            row += 1

        # Adjust column widths
        exp_worksheet.set_column(0, 0, 12)
        exp_worksheet.set_column(1, 1, 25)
        exp_worksheet.set_column(2, 31, 8)

        # Add statistics worksheet
        stats_worksheet = workbook.add_worksheet("Statistics")

        # Write title
        row = 0
        stats_worksheet.merge_range(row, 0, row, 5, f"{subject.subject_name.upper()} - STATISTICS", header_format)
        row += 1

        # Calculate statistics
        total_students = len(students)

        # Lists to store marks for calculations
        exp_marks_list = []
        practical_marks_list = []
        class_test_marks_list = []
        sla_marks_list = []
        total_marks_list = []

        for student in students:
            # Get experiment marks
            manual_marks = ManualMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).all()

            exp_total = sum(mark.marks_obtained for mark in manual_marks)
            exp_marks_list.append(exp_total)

            # Get practical exam marks
            practical_mark = PracticalMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).first()

            practical_value = practical_mark.practical_exam_marks if practical_mark else 0
            practical_marks_list.append(practical_value)

            # Get class test marks
            class_test = ClassTestMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).first()

            ct_avg = 0
            if class_test:
                ct_avg = (class_test.class_test_1 + class_test.class_test_2) / 2
            class_test_marks_list.append(ct_avg)

            # Get SLA marks
            sla_mark = SLAMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).first()

            sla_total = 0
            if sla_mark:
                sla_total = sla_mark.micro_project + sla_mark.assignment + sla_mark.other_marks
            sla_marks_list.append(sla_total)

            # Calculate total
            total_marks = exp_total + practical_value + ct_avg + sla_total
            total_marks_list.append(total_marks)

        # Write statistics
        stats_worksheet.write(row, 0, "Statistic", subheader_format)
        stats_worksheet.write(row, 1, "Experiments", subheader_format)
        stats_worksheet.write(row, 2, "Practical", subheader_format)
        stats_worksheet.write(row, 3, "Class Tests", subheader_format)
        stats_worksheet.write(row, 4, "SLA", subheader_format)
        stats_worksheet.write(row, 5, "Total", subheader_format)
        row += 1

        # Average
        stats_worksheet.write(row, 0, "Average", cell_format)
        if exp_marks_list:
            stats_worksheet.write(row, 1, sum(exp_marks_list) / len(exp_marks_list), cell_format)
        else:
            stats_worksheet.write(row, 1, 0, cell_format)

        if practical_marks_list:
            stats_worksheet.write(row, 2, sum(practical_marks_list) / len(practical_marks_list), cell_format)
        else:
            stats_worksheet.write(row, 2, 0, cell_format)

        if class_test_marks_list:
            stats_worksheet.write(row, 3, sum(class_test_marks_list) / len(class_test_marks_list), cell_format)
        else:
            stats_worksheet.write(row, 3, 0, cell_format)

        if sla_marks_list:
            stats_worksheet.write(row, 4, sum(sla_marks_list) / len(sla_marks_list), cell_format)
        else:
            stats_worksheet.write(row, 4, 0, cell_format)

        if total_marks_list:
            stats_worksheet.write(row, 5, sum(total_marks_list) / len(total_marks_list), cell_format)
        else:
            stats_worksheet.write(row, 5, 0, cell_format)

        row += 1

        # Max
        stats_worksheet.write(row, 0, "Maximum", cell_format)
        stats_worksheet.write(row, 1, max(exp_marks_list) if exp_marks_list else 0, cell_format)
        stats_worksheet.write(row, 2, max(practical_marks_list) if practical_marks_list else 0, cell_format)
        stats_worksheet.write(row, 3, max(class_test_marks_list) if class_test_marks_list else 0, cell_format)
        stats_worksheet.write(row, 4, max(sla_marks_list) if sla_marks_list else 0, cell_format)
        stats_worksheet.write(row, 5, max(total_marks_list) if total_marks_list else 0, cell_format)
        row += 1

        # Min
        stats_worksheet.write(row, 0, "Minimum", cell_format)
        stats_worksheet.write(row, 1, min(exp_marks_list) if exp_marks_list else 0, cell_format)
        stats_worksheet.write(row, 2, min(practical_marks_list) if practical_marks_list else 0, cell_format)
        stats_worksheet.write(row, 3, min(class_test_marks_list) if class_test_marks_list else 0, cell_format)
        stats_worksheet.write(row, 4, min(sla_marks_list) if sla_marks_list else 0, cell_format)
        stats_worksheet.write(row, 5, min(total_marks_list) if total_marks_list else 0, cell_format)
        row += 1

        # Adjust column widths
        stats_worksheet.set_column(0, 0, 15)
        stats_worksheet.set_column(1, 5, 12)

        # Save the workbook
        writer.close()

        return file_path

    @staticmethod
    def _generate_subject_pdf_report(subject, students):
        """Generate a PDF report focused on a specific subject."""
        from app.models import ManualMarks, PracticalMarks, ClassTestMarks, SLAMarks

        # Create filename
        filename = f"subject_{subject.subject_id}_{subject.subject_name}_report_{datetime.now().strftime('%Y%m%d')}.pdf"

        # Create PDF
        class PDF(FPDF):
            def __init__(self):
                super().__init__(orientation='L')  # Landscape orientation
                self.set_auto_page_break(auto=True, margin=15)

            def header(self):
                # Add logo if it exists
                if os.path.exists(ReportingModule.LOGO_PATH):
                    self.image(ReportingModule.LOGO_PATH, 10, 8, 25)
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, f"{subject.subject_name.upper()} - SUBJECT REPORT", 0, 1, 'C')
                self.set_font('Arial', 'I', 10)
                self.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'C')
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

            def create_table(self, headers, data, col_widths):
                # Headers
                self.set_font('Arial', 'B', 10)
                self.set_fill_color(*ReportingModule.COLORS["subheader_bg"])
                self.set_text_color(*ReportingModule.COLORS["header_text"])

                for i, header in enumerate(headers):
                    self.cell(col_widths[i], 10, str(header), 1, 0, 'C', True)
                self.ln()

                # Data
                self.set_font('Arial', '', 9)
                self.set_text_color(0, 0, 0)

                for row in data:
                    for i, value in enumerate(row):
                        self.cell(col_widths[i], 8, str(value), 1, 0, 'C')
                    self.ln()

                self.ln(5)

        # Create PDF instance
        pdf = PDF()
        pdf.add_page()

        # ----- Subject Overview Section -----
        pdf.section_title(f"SUBJECT OVERVIEW - {subject.subject_name} (Year {subject.year})")

        # Create table
        headers = [
            'Student ID',
            'Name',
            'Exp. Marks',
            'Practical',
            'Class Test Avg',
            'SLA Total',
            'Overall'
        ]
        col_widths = [25, 60, 35, 35, 35, 35, 35]

        data = []

        # Collect all data and calculate statistics
        exp_marks_list = []
        practical_marks_list = []
        class_test_marks_list = []
        sla_marks_list = []
        total_marks_list = []

        for student in students:
            # Get experiment marks
            manual_marks = ManualMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).all()

            exp_total = sum(mark.marks_obtained for mark in manual_marks)
            exp_marks_list.append(exp_total)

            # Get practical exam marks
            practical_mark = PracticalMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).first()

            practical_value = practical_mark.practical_exam_marks if practical_mark else 0
            practical_marks_list.append(practical_value)

            # Get class test marks
            class_test = ClassTestMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).first()

            ct_avg = 0
            if class_test:
                ct_avg = (class_test.class_test_1 + class_test.class_test_2) / 2
            class_test_marks_list.append(ct_avg)

            # Get SLA marks
            sla_mark = SLAMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).first()

            sla_total = 0
            if sla_mark:
                sla_total = sla_mark.micro_project + sla_mark.assignment + sla_mark.other_marks
            sla_marks_list.append(sla_total)

            # Calculate total
            total_marks = exp_total + practical_value + ct_avg + sla_total
            total_marks_list.append(total_marks)

            data.append([
                student.student_id,
                student.name,
                exp_total,
                practical_value,
                f"{ct_avg:.2f}",
                sla_total,
                total_marks
            ])

        pdf.create_table(headers, data, col_widths)

        # ----- Statistics Section -----
        pdf.section_title("STATISTICS")

        headers = ['Statistic', 'Experiments', 'Practical', 'Class Tests', 'SLA', 'Total']
        col_widths = [40, 40, 40, 40, 40, 40]

        # Calculate statistics
        data = []

        # Average
        avg_row = ["Average"]
        avg_row.append(f"{sum(exp_marks_list) / len(exp_marks_list):.2f}" if exp_marks_list else "0")
        avg_row.append(f"{sum(practical_marks_list) / len(practical_marks_list):.2f}" if practical_marks_list else "0")
        avg_row.append(
            f"{sum(class_test_marks_list) / len(class_test_marks_list):.2f}" if class_test_marks_list else "0")
        avg_row.append(f"{sum(sla_marks_list) / len(sla_marks_list):.2f}" if sla_marks_list else "0")
        avg_row.append(f"{sum(total_marks_list) / len(total_marks_list):.2f}" if total_marks_list else "0")
        data.append(avg_row)

        # Maximum
        max_row = ["Maximum"]
        max_row.append(f"{max(exp_marks_list):.2f}" if exp_marks_list else "0")
        max_row.append(f"{max(practical_marks_list):.2f}" if practical_marks_list else "0")
        max_row.append(f"{max(class_test_marks_list):.2f}" if class_test_marks_list else "0")
        max_row.append(f"{max(sla_marks_list):.2f}" if sla_marks_list else "0")
        max_row.append(f"{max(total_marks_list):.2f}" if total_marks_list else "0")
        data.append(max_row)

        # Minimum
        min_row = ["Minimum"]
        min_row.append(f"{min(exp_marks_list):.2f}" if exp_marks_list else "0")
        min_row.append(f"{min(practical_marks_list):.2f}" if practical_marks_list else "0")
        min_row.append(f"{min(class_test_marks_list):.2f}" if class_test_marks_list else "0")
        min_row.append(f"{min(sla_marks_list):.2f}" if sla_marks_list else "0")
        min_row.append(f"{min(total_marks_list):.2f}" if total_marks_list else "0")
        data.append(min_row)

        # Standard Deviation
        import statistics
        std_row = ["Std Deviation"]
        std_row.append(f"{statistics.stdev(exp_marks_list):.2f}" if len(exp_marks_list) > 1 else "N/A")
        std_row.append(f"{statistics.stdev(practical_marks_list):.2f}" if len(practical_marks_list) > 1 else "N/A")
        std_row.append(f"{statistics.stdev(class_test_marks_list):.2f}" if len(class_test_marks_list) > 1 else "N/A")
        std_row.append(f"{statistics.stdev(sla_marks_list):.2f}" if len(sla_marks_list) > 1 else "N/A")
        std_row.append(f"{statistics.stdev(total_marks_list):.2f}" if len(total_marks_list) > 1 else "N/A")
        data.append(std_row)

        pdf.create_table(headers, data, col_widths)

        # ----- Grade Distribution Section -----
        pdf.section_title("GRADE DISTRIBUTION")

        # Define grade boundaries
        grade_boundaries = {
            'A+': 90,
            'A': 80,
            'B+': 75,
            'B': 70,
            'C+': 65,
            'C': 60,
            'D': 50,
            'F': 0
        }

        # Count grades
        grade_counts = {grade: 0 for grade in grade_boundaries}

        for total in total_marks_list:
            for grade, min_mark in grade_boundaries.items():
                if total >= min_mark:
                    grade_counts[grade] += 1
                    break

        # Create grade distribution table
        headers = ['Grade', 'Range', 'Count', 'Percentage']
        col_widths = [40, 60, 40, 60]

        data = []
        total_students = len(students)

        prev_boundary = 100
        for grade, boundary in grade_boundaries.items():
            count = grade_counts[grade]
            percentage = (count / total_students * 100) if total_students > 0 else 0

            if grade == 'A+':
                range_str = f"{boundary}% - 100%"
            else:
                next_grade = list(grade_boundaries.keys())[list(grade_boundaries.keys()).index(grade) - 1]
                next_boundary = grade_boundaries[next_grade]
                range_str = f"{boundary}% - {next_boundary - 0.01}%"

            data.append([
                grade,
                range_str,
                count,
                f"{percentage:.2f}%"
            ])

        pdf.create_table(headers, data, col_widths)

        # ----- Performance Graph Section -----
        pdf.section_title("PERFORMANCE VISUALIZATION")

        # Create visualization using matplotlib
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            from io import BytesIO

            # Set the style
            plt.style.use('ggplot')

            # Create a temporary file for the graph
            temp_graph_path = os.path.join(ReportingModule.REPORTS_DIR, f"temp_graph_{subject.subject_id}.png")

            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

            # 1. Box plot of different assessment components
            assessment_data = [exp_marks_list, practical_marks_list, class_test_marks_list, sla_marks_list]
            ax1.boxplot(assessment_data)
            ax1.set_title('Assessment Component Distribution')
            ax1.set_xticklabels(['Experiments', 'Practical', 'Class Tests', 'SLA'])
            ax1.set_ylabel('Marks')

            # 2. Grade distribution pie chart
            grades = list(grade_counts.keys())
            counts = list(grade_counts.values())

            # Filter out grades with zero counts
            non_zero_indices = [i for i, count in enumerate(counts) if count > 0]
            grades = [grades[i] for i in non_zero_indices]
            counts = [counts[i] for i in non_zero_indices]

            ax2.pie(counts, labels=grades, autopct='%1.1f%%', startangle=90)
            ax2.set_title('Grade Distribution')
            ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

            plt.tight_layout()

            # Save the plot
            plt.savefig(temp_graph_path, dpi=300, bbox_inches='tight')
            plt.close()

            # Add the graph to the PDF
            pdf.image(temp_graph_path, x=pdf.w / 2 - 80, y=None, w=160)

            # Delete temporary file
            os.remove(temp_graph_path)

        except Exception as e:
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 10, f"Error generating visualization: {str(e)}", 0, 1, 'C')

        # ----- Individual Student Reports -----
        for student in students:
            pdf.add_page()
            pdf.section_title(f"INDIVIDUAL STUDENT REPORT - {student.name} ({student.student_id})")

            # Get student data
            manual_marks = ManualMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).all()

            practical_mark = PracticalMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).first()

            class_test = ClassTestMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).first()

            sla_mark = SLAMarks.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).first()

            # Student summary
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(40, 10, "Summary:", 0, 0)
            pdf.set_font('Arial', '', 11)
            pdf.ln(10)

            # Calculate totals
            exp_total = sum(mark.marks_obtained for mark in manual_marks)
            practical_value = practical_mark.practical_exam_marks if practical_mark else 0

            ct1 = class_test.class_test_1 if class_test else 0
            ct2 = class_test.class_test_2 if class_test else 0
            ct_avg = (ct1 + ct2) / 2 if (class_test and (ct1 or ct2)) else 0

            sla_total = 0
            if sla_mark:
                sla_total = sla_mark.micro_project + sla_mark.assignment + sla_mark.other_marks

            total_marks = exp_total + practical_value + ct_avg + sla_total

            # Determine grade
            student_grade = "F"
            for grade, boundary in grade_boundaries.items():
                if total_marks >= boundary:
                    student_grade = grade
                    break

            # Create summary table
            headers = ['Component', 'Marks Obtained', 'Average', 'Max Possible', 'Percentile']
            col_widths = [50, 40, 40, 40, 40]

            # Calculate percentiles
            def percentile_rank(score, scores):
                if not scores:
                    return "N/A"
                return f"{len([s for s in scores if s < score]) / len(scores) * 100:.1f}%"

            data = [
                ["Experiments", exp_total,
                 f"{sum(exp_marks_list) / len(exp_marks_list):.2f}" if exp_marks_list else "0",
                 f"{max(exp_marks_list) if exp_marks_list else 0}",
                 percentile_rank(exp_total, exp_marks_list)],

                ["Practical Exam", practical_value,
                 f"{sum(practical_marks_list) / len(practical_marks_list):.2f}" if practical_marks_list else "0",
                 f"{max(practical_marks_list) if practical_marks_list else 0}",
                 percentile_rank(practical_value, practical_marks_list)],

                ["Class Tests (Avg)", f"{ct_avg:.2f}",
                 f"{sum(class_test_marks_list) / len(class_test_marks_list):.2f}" if class_test_marks_list else "0",
                 f"{max(class_test_marks_list) if class_test_marks_list else 0}",
                 percentile_rank(ct_avg, class_test_marks_list)],

                ["SLA Components", sla_total,
                 f"{sum(sla_marks_list) / len(sla_marks_list):.2f}" if sla_marks_list else "0",
                 f"{max(sla_marks_list) if sla_marks_list else 0}",
                 percentile_rank(sla_total, sla_marks_list)],

                ["TOTAL", total_marks,
                 f"{sum(total_marks_list) / len(total_marks_list):.2f}" if total_marks_list else "0",
                 f"{max(total_marks_list) if total_marks_list else 0}",
                 percentile_rank(total_marks, total_marks_list)]
            ]

            pdf.create_table(headers, data, col_widths)

            # Add grade information
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"Final Grade: {student_grade}", 0, 1, 'C')

            # Detailed experiment marks
            pdf.ln(5)
            pdf.section_title("DETAILED EXPERIMENT MARKS")

            if manual_marks:
                headers = ['Experiment #', 'Date', 'Marks', 'Max Marks', 'Percentage']
                col_widths = [30, 50, 30, 30, 30]

                data = []
                for mark in manual_marks:
                    percentage = (mark.marks_obtained / mark.max_marks * 100) if mark.max_marks else 0
                    data.append([
                        mark.experiment_number,
                        mark.date.strftime('%Y-%m-%d') if hasattr(mark, 'date') and mark.date else "N/A",
                        mark.marks_obtained,
                        mark.max_marks,
                        f"{percentage:.2f}%"
                    ])

                pdf.create_table(headers, data, col_widths)
            else:
                pdf.set_font('Arial', 'I', 10)
                pdf.cell(0, 10, "No experiment marks recorded", 0, 1, 'C')

        # Save PDF
        os.makedirs(ReportingModule.REPORTS_DIR, exist_ok=True)
        file_path = os.path.join(ReportingModule.REPORTS_DIR, filename)
        pdf.output(file_path)

        return file_path
