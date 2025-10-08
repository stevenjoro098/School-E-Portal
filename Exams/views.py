from django.views import View
from django.views.generic import ListView, CreateView
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Avg
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.reverse import reverse_lazy
from openpyxl import Workbook
from weasyprint import HTML

from Subjects.models import Subject, Grade
from .models import Exam, StudentPerformance
from Students.models import Student

class GradesList(ListView):
    template_name = 'grade_list.html'
    model = Grade
    context_object_name = 'grades_list'

class CreateExam(CreateView):
    template_name = 'create_exam.html'
    model = Exam
    fields = ['*']
    success_url = reverse_lazy('exams')


class ExamsList(ListView):
    template_name = 'exams_list.html'
    model = Exam
    context_object_name = 'exams_list'

    def get_queryset(self):
        grade = get_object_or_404(Grade, pk=self.kwargs['pk'])
        return Exam.objects.filter(grade=grade)


class EnterExamPerformanceView(View):
    template_name = "enter_performance.html"

    def get(self, request, pk):
        exam = get_object_or_404(Exam, id=pk)
        students = Student.objects.filter(grade=exam.grade)
        subjects = Subject.objects.filter(grade=exam.grade)

        context = {
            "exam": exam,
            "students": students,
            "subjects": subjects,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        exam = get_object_or_404(Exam, id=pk)
        students = Student.objects.filter(grade=exam.grade)
        subjects = Subject.objects.filter(grade=exam.grade)

        for student in students:
            for subject in subjects:
                field_name = f"perf_{student.id}_{subject.id}"
                score = request.POST.get(field_name)

                if score and score.isdigit():
                    StudentPerformance.objects.update_or_create(
                        student=student,
                        exam=exam,
                        subject=subject,
                        defaults={"performance": int(score)},
                    )

        return redirect("enter_exam_performance", pk=exam.id)


class ExamPerformanceListView(View):
    template_name = "performance_list.html"

    def get(self, request, pk):
        exam = get_object_or_404(Exam, id=pk)
        students = Student.objects.filter(grade=exam.grade)
        subjects = Subject.objects.filter(grade=exam.grade)

        performance_data = []

        # Collect scores for each student
        for student in students:
            scores = {}
            for subject in subjects:
                perf = StudentPerformance.objects.filter(
                    exam=exam, student=student, subject=subject
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
            "grade": exam.grade,
            "subjects": subjects,
            "performance_data": performance_data,
            "subject_averages": subject_averages,
        }
        return render(request, self.template_name, context)


class ExportExamExcelView(View):
    def get(self, request, pk):
        exam = get_object_or_404(Exam, id=pk)
        students = Student.objects.filter(grade=exam.grade)
        subjects = Subject.objects.filter(grade=exam.grade)

        # same logic to prepare performance_data
        performance_data = []
        for student in students:
            scores = {}
            for subject in subjects:
                perf = StudentPerformance.objects.filter(
                    exam=exam, student=student, subject=subject
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
        header = ["Rank", "Student"] + [s.name for s in subjects] + ["Total", "Average"]
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
        subjects = Subject.objects.filter(grade=exam.grade)
        students = Student.objects.filter(grade=exam.grade)
        num_subjects = subjects.count()

        # Compute performances
        student_data = []
        for student in students:
            performances = StudentPerformance.objects.filter(exam=exam, student=student)
            total_score = performances.aggregate(total=Sum("performance"))["total"] or 0
            subj_scores = {p.subject.id: p.performance for p in performances}

            # 🔹 Learner mean = total ÷ number of subjects
            mean_score = total_score / num_subjects if num_subjects > 0 else 0

            student_data.append({
                "student": student,
                "total": total_score,
                "mean": mean_score,
                "scores": subj_scores,
            })

        # Rank by total descending
        ranked_students = sorted(student_data, key=lambda x: x["total"], reverse=True)

        # Compute averages per subject
        subject_averages = {
            subj.id: StudentPerformance.objects.filter(exam=exam, subject=subj).aggregate(avg=Avg("performance"))["avg"] or 0
            for subj in subjects
        }

        # 🔹 Compute class mean score
        class_total = sum(s["total"] for s in student_data)
        num_students = len(student_data)
        class_mean_score = class_total / num_students if num_students > 0 else 0

        # Render to HTML
        html_string = render_to_string("exam_performance_pdf.html", {
            "exam": exam,
            "subjects": subjects,
            "ranked_students": ranked_students,
            "subject_averages": subject_averages,
            "class_mean_score": class_mean_score,  # overall class mean
        })

        pdf_file = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{exam.exam_name}_{exam.grade}_performances.pdf"'
        return response


class StudentPerformanceDetailView(View):
    template_name = "student_performance_details.html"

    def get(self, request, id, pk):
        exam = get_object_or_404(Exam, id=id)
        student = get_object_or_404(Student, id=pk)

        # Get subjects for the grade
        subjects = Subject.objects.filter(grade=exam.grade)

        # Fetch performances for this student
        performances = StudentPerformance.objects.filter(exam=exam, student=student)

        scores = {p.subject.id: p.performance for p in performances}
        total = sum(scores.values())
        average = round(total / subjects.count(), 2) if subjects else 0

        context = {
            "exam": exam,
            "student": student,
            "subjects": subjects,
            "scores": scores,
            "total": total,
            "average": average,
        }
        return render(request, self.template_name, context)

from django.db.models import Sum

class ExportStudentPDFView(View):
    def get(self, request, exam_id, student_id):
        exam = get_object_or_404(Exam, pk=exam_id)
        student = get_object_or_404(Student, pk=student_id)
        subjects = Subject.objects.filter(grade=exam.grade)

        # ✅ Get performances for this student
        performances = StudentPerformance.objects.filter(exam=exam, student=student)
        scores = {p.subject.id: p.performance for p in performances}
        total = sum(scores.values())
        average = round(total / subjects.count(), 2) if subjects else 0

        # ✅ Calculate ranking
        all_totals = (
            StudentPerformance.objects.filter(exam=exam)
            .values("student")
            .annotate(total_score=Sum("performance"))
            .order_by("-total_score")
        )

        # Map student_id → rank
        rank = None
        for idx, record in enumerate(all_totals, start=1):
            if record["student"] == student.id:
                rank = idx
                break

        total_students = all_totals.count()

        context = {
            "exam": exam,
            "student": student,
            "subjects": subjects,
            "scores": scores,
            "total": total,
            "average": average,
            "rank": rank,
            "total_students": total_students,
        }

        html_string = render_to_string("student_report_pdf.html", context)
        pdf_file = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="{student.first_name}_{student.second_name}_{exam.exam_name}_Report.pdf"'
        )
        return response

class ExportClassPDFView(View):
    def get(self, request, exam_id):
        exam = get_object_or_404(Exam, pk=exam_id)
        subjects = Subject.objects.filter(grade=exam.grade)
        students = Student.objects.filter(grade=exam.grade).order_by("first_name")

        # ✅ Precompute totals for all students
        all_totals = (
            StudentPerformance.objects.filter(exam=exam)
            .values("student")
            .annotate(total_score=Sum("performance"))
            .order_by("-total_score")
        )

        # Make student_id → rank lookup
        rank_lookup = {}
        for idx, record in enumerate(all_totals, start=1):
            rank_lookup[record["student"]] = idx

        total_students = students.count()

        # ✅ Build pages for each student
        all_html = ""
        for student in students:
            performances = StudentPerformance.objects.filter(exam=exam, student=student)
            scores = {p.subject.id: p.performance for p in performances}
            total = sum(scores.values())
            average = round(total / subjects.count(), 2) if subjects else 0
            rank = rank_lookup.get(student.id, None)

            context = {
                "exam": exam,
                "student": student,
                "subjects": subjects,
                "scores": scores,
                "total": total,
                "average": average,
                "rank": rank,
                "total_students": total_students,
            }

            # Add page break after each student (except last)
            html_string = render_to_string("student_report_pdf.html", context)
            all_html += html_string + '<p style="page-break-after: always;"></p>'

        # ✅ Generate one combined PDF
        pdf_file = HTML(string=all_html).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{exam.exam_name}_{ exam.term }_Class_Report.pdf"'
        return response
