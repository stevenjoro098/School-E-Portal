from django.views import View
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect

import io
from django.http import HttpResponse
from django.db.models import Sum, Avg
from openpyxl import Workbook
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML

from .models import Exam, ExamSubject, StudentPerformance
from Students.models import Student

class ExamsList(ListView):
    template_name = 'exams_list.html'
    model = Exam
    context_object_name = 'exams_list'

class EnterExamPerformanceView(View):
    template_name = "enter_performance.html"

    def get(self, request, pk):
        exam = get_object_or_404(Exam, id=pk)
        students = Student.objects.filter(grade=exam.grade)
        subjects = exam.exam_subjects.all()

        context = {
            "exam": exam,
            "students": students,
            "subjects": subjects,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        exam = get_object_or_404(Exam, id=pk)
        students = Student.objects.filter(grade=exam.grade)
        subjects = exam.exam_subjects.all()

        for student in students:
            for subject in subjects:
                field_name = f"perf_{student.id}_{subject.id}"
                score = request.POST.get(field_name)

                if score and score.isdigit():
                    StudentPerformance.objects.update_or_create(
                        student=student,
                        exam_subject=subject,
                        exam=exam,
                        defaults={"performance": int(score)},
                    )

        return redirect("enter_exam_performance", pk=exam.id)

class ExamPerformanceListView(View):
    template_name = "performance_list.html"

    def get(self, request, pk):
        exam = get_object_or_404(Exam, id=pk)
        students = Student.objects.filter(grade=exam.grade)
        subjects = exam.exam_subjects.all()

        performance_data = []

        # Collect scores for each student
        for student in students:
            scores = {}
            for subject in subjects:
                perf = StudentPerformance.objects.filter(
                    exam=exam, student=student, exam_subject=subject
                ).first()
                scores[subject.id] = perf.performance if perf else None

            total = sum([s for s in scores.values() if s is not None])
            avg = total / len(subjects) if subjects else 0

            performance_data.append({
                "student": student,
                "scores": scores,
                "total": total,
                "average": round(avg, 2),
            })

        # ✅ Sort students by total score (highest first)
        performance_data = sorted(performance_data, key=lambda x: x["total"], reverse=True)

        # ✅ Calculate average per subject across all students
        subject_averages = {}
        for subject in subjects:
            values = [row["scores"][subject.id] for row in performance_data if row["scores"][subject.id] is not None]
            subject_averages[subject.id] = round(sum(values) / len(values), 2) if values else None

        context = {
            "exam": exam,
            "subjects": subjects,
            "performance_data": performance_data,
            "subject_averages": subject_averages,
        }
        return render(request, self.template_name, context)


class ExportExamExcelView(View):

    def get(self, request, pk):
        exam = get_object_or_404(Exam, id=pk)
        students = Student.objects.filter(grade=exam.grade)
        subjects = exam.exam_subjects.all()

        # same logic to prepare performance_data
        performance_data = []
        for student in students:
            scores = {}
            for subject in subjects:
                perf = StudentPerformance.objects.filter(
                    exam=exam, student=student, exam_subject=subject
                ).first()
                scores[subject.id] = perf.performance if perf else None
            total = sum([s for s in scores.values() if s is not None])
            avg = total / len(subjects) if subjects else 0
            performance_data.append({
                "student": student,
                "scores": scores,
                "total": total,
                "average": round(avg, 2),
            })
        performance_data = sorted(performance_data, key=lambda x: x["total"], reverse=True)

        # Create Excel workbook
        wb = Workbook()
        ws = wb.active
        ws.title = f"{exam.exam_name}"

        # Header row
        header = ["Rank", "Student"] + [s.exam_subject for s in subjects] + ["Total", "Average"]
        ws.append(header)

        # Student rows
        for idx, row in enumerate(performance_data, start=1):
            data_row = [
                idx,
                f"{row['student'].first_name} {row['student'].second_name}"
            ] + [row["scores"].get(s.id, "") for s in subjects] + [row["total"], row["average"]]
            ws.append(data_row)

        # Response
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="{exam.exam_name}.xlsx"'
        wb.save(response)
        return response


class ExportExamPDFView(View):
    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        subjects = exam.exam_subjects.all()
        students = Student.objects.filter(grade=exam.grade)

        # Compute performances
        student_data = []
        for student in students:
            performances = StudentPerformance.objects.filter(exam=exam, student=student)
            total_score = performances.aggregate(total=Sum("performance"))["total"] or 0
            subj_scores = {p.exam_subject.id: p.performance for p in performances}
            student_data.append({
                "student": student,
                "total": total_score,
                "scores": subj_scores,
            })

        # Rank by total descending
        ranked_students = sorted(student_data, key=lambda x: x["total"], reverse=True)

        # Compute averages per subject
        subject_averages = {
            subj.id: StudentPerformance.objects.filter(exam=exam, exam_subject=subj).aggregate(avg=Avg("performance"))["avg"] or 0
            for subj in subjects
        }

        # Render to HTML
        html_string = render_to_string("exam_performance_pdf.html", {
            "exam": exam,
            "subjects": subjects,
            "ranked_students": ranked_students,
            "subject_averages": subject_averages,
        })

        pdf_file = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{exam.exam_name}_{exam.grade}_performances.pdf"'
        return response
