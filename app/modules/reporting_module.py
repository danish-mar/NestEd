import os
import pandas as pd
from fpdf import FPDF
from app.models import Student, Marks

class ReportingModule:
    """Handles report generation for students and their marks."""

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get absolute path of this file
    REPORTS_DIR = os.path.join(BASE_DIR, "..", "reports")  # Store reports in the root-level "reports" folder

    @staticmethod
    def generate_student_report(file_format="excel"):
        """Generate a report for all students and their marks."""
        students = Student.query.all()
        data = ReportingModule._get_student_marks_data(students)

        if file_format == "excel":
            return ReportingModule._generate_excel(data, "student_report.xlsx")
        elif file_format == "pdf":
            return ReportingModule._generate_pdf(data, "student_report.pdf")

    @staticmethod
    def generate_single_student_report(student_id, file_format="excel"):
        """Generate a report for a specific student and their marks."""
        student = Student.query.get(student_id)
        if not student:
            return None  # Student not found

        data = ReportingModule._get_student_marks_data([student])

        if file_format == "excel":
            return ReportingModule._generate_excel(data, f"student_{student_id}_report.xlsx")
        elif file_format == "pdf":
            return ReportingModule._generate_pdf(data, f"student_{student_id}_report.pdf")

    @staticmethod
    def _get_student_marks_data(students):
        """Helper function to fetch student and marks data."""
        data = []
        for student in students:
            marks = Marks.query.filter_by(student_id=student.student_id).all()
            for mark in marks:
                data.append({
                    "Student ID": student.student_id,
                    "Name": student.name,
                    "Email": student.email,
                    "Phone": student.phone,
                    "Admission Year": student.admission_year,
                    "Subject": mark.subject.subject_name if mark.subject else "N/A",
                    "Oral Marks (D1)": mark.d1_oral,
                    "Practical Marks (D2)": mark.d2_practical,
                    "Theory Marks (D3)": mark.d3_theory,
                    "Total Marks": mark.total_marks,
                })
        return data

    @staticmethod
    def _generate_excel(data, filename):
        """Generate an Excel file from the given data."""
        df = pd.DataFrame(data)
        os.makedirs(ReportingModule.REPORTS_DIR, exist_ok=True)  # Ensure reports folder exists
        file_path = os.path.join(ReportingModule.REPORTS_DIR, filename)
        df.to_excel(file_path, index=False)
        return file_path

    @staticmethod
    def _generate_pdf(data, filename):
        """Generate a PDF file from the given data."""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, "Student Marks Report", ln=True, align="C")

        pdf.set_font("Arial", "", 10)

        for record in data:
            pdf.ln(5)
            for key, value in record.items():
                pdf.cell(200, 7, f"{key}: {value}", ln=True)
            pdf.ln(5)
            pdf.cell(200, 0, "", "B", ln=True)  # Line Separator

        os.makedirs(ReportingModule.REPORTS_DIR, exist_ok=True)  # Ensure reports folder exists
        file_path = os.path.join(ReportingModule.REPORTS_DIR, filename)
        pdf.output(file_path)
        return file_path
