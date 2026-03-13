from collections import defaultdict
from django.views import View
from django.views.generic import ListView, CreateView, TemplateView
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Avg
from django.http import HttpResponse
from django.contrib import messages
from django.template.loader import render_to_string
from rest_framework.reverse import reverse_lazy
from openpyxl import Workbook
from weasyprint import HTML
from django.conf import settings
import os

from Subjects.models import Subject, Grade
from .models import Exam, StudentPerformance
from Students.models import Student, Teachers
#from .utils.cbc_kjsea_points import score_to_cbc


class GradesList(ListView):
    template_name = 'grade_list.html'
    model = Grade
    context_object_name = 'grades_list'

class CreateExam(CreateView):
    template_name = 'create_exam.html'
    model = Exam
    fields = ['exam_name','term','grade']
    success_url = reverse_lazy('exams')



class ExamsList(ListView):
    template_name = 'exams_list.html'
    model = Exam
    context_object_name = 'exams_list'

    def get_queryset(self):
        self.grade = get_object_or_404(Grade, pk=self.kwargs['pk'])
        return Exam.objects.filter(grade=self.grade).order_by('term', 'created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exams = context['exams_list']

        # ✅ Group exams by term
        grouped_exams = defaultdict(list)
        for exam in exams:
            grouped_exams[exam.term].append(exam)

        context['grouped_exams'] = dict(grouped_exams)
        context['grade'] = self.grade
        return context


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
        messages.success(request, "Performance Added Success")
        return redirect("enter_exam_performance", pk=exam.id)


from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Exam, Student, Subject, StudentPerformance


class ExamPerformanceListView(View):
    template_name = "performance_list.html"

    def get(self, request, pk):
        exam = get_object_or_404(Exam, id=pk)

        students = Student.objects.filter(grade=exam.grade)
        subjects = Subject.objects.filter(grade=exam.grade)

        # Fetch all performances in ONE query
        performances = StudentPerformance.objects.filter(
            exam=exam,
            student__in=students,
            subject__in=subjects
        )

        # Map: (student_id, subject_id) -> raw score
        perf_map = {
            (p.student_id, p.subject_id): p.performance
            for p in performances
        }

        performance_data = []

        for student in students:
            scores = {}
            total = 0
            count = 0

            for subject in subjects:
                score = perf_map.get((student.id, subject.id))

                scores[subject.id] = score

                if score is not None:
                    total += score
                    count += 1

            average = round(total / count, 2) if count else 0

            performance_data.append({
                "student": student,
                "scores": scores,
                "total": total,
                "average": average,
            })

        # Rank by total marks
        performance_data.sort(key=lambda x: x["total"], reverse=True)

        # Subject averages (raw marks)
        subject_averages = {}
        for subject in subjects:
            subject_scores = [
                row["scores"][subject.id]
                for row in performance_data
                if row["scores"][subject.id] is not None
            ]
            subject_averages[subject.id] = (
                round(sum(subject_scores) / len(subject_scores), 2)
                if subject_scores else None
            )

        context = {
            "exam": exam,
            "grade": exam.grade,
            "subjects": subjects,
            "performance_data": performance_data,
            "subject_averages": subject_averages,
        }

        return render(request, self.template_name, context)

class StudentSingleExamPDF(View):
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


        html_string = render_to_string("pdf/student_performance_pdf.html", context = {
            "exam": exam,
            "student": student,
            "subjects": subjects,
            "scores": scores,
            "total": total,
            "average": average,
        })

        pdf_file = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{student}_{exam.exam_name}_{exam.grade}_performance.pdf"'
        return response

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

class TeacherSubjectExamPerformanceView(TemplateView):
    template_name = 'teacher_subjects_performance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        teacher = get_object_or_404(Teachers, pk=kwargs['teacher_id'])

        performances = (
            StudentPerformance.objects
            .filter(subject__teacher=teacher)
            .values(
                'exam__id',
                'exam__exam_name',
                'exam__grade__name',
                'exam__term',
                'subject__id',
                'subject__name'
            )
            .annotate(average_score=Avg('performance'))
            .order_by('exam__created', 'subject__name')
        )

        context.update({
            'teacher': teacher,
            'performances': performances
        })

        return context



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

class StudentTermExamSummaryView(View):
    template_name = "student_term_exam_summary.html"

    def get(self, request, exam_id, student_id):
        # Get reference exam, student and grade
        exam = get_object_or_404(Exam, pk=exam_id)
        student = get_object_or_404(Student, pk=student_id)
        grade = exam.grade
        subjects = Subject.objects.filter(grade=grade).order_by("name")

        # ✅ Get all exams in the same term and grade
        term_exams = Exam.objects.filter(term=exam.term, grade=grade).order_by("created")

        # Build scores per exam
        scores_by_exam = {}
        totals = {}
        averages = {}
        ranks = {}

        for e in term_exams:
            performances = StudentPerformance.objects.filter(exam=e, student=student)
            scores_by_exam[e.id] = {p.subject.id: p.performance for p in performances}

            total = sum(scores_by_exam[e.id].values())
            avg = round(total / subjects.count(), 2) if subjects.exists() else 0
            totals[e.id] = total
            averages[e.id] = avg

            # Ranking
            all_totals = (
                StudentPerformance.objects.filter(exam=e)
                .values("student")
                .annotate(total_score=Sum("performance"))
                .order_by("-total_score")
            )
            rank = next(
                (idx for idx, record in enumerate(all_totals, start=1)
                 if record["student"] == student.id),
                None
            )
            ranks[e.id] = rank

        context = {
            "exam": exam,
            "student": student,
            "subjects": subjects,
            "term_exams": term_exams,
            "scores_by_exam": scores_by_exam,
            "totals": totals,
            "averages": averages,
            "ranks": ranks,
        }

        return render(request, self.template_name, context)


class PrintTermReportCardsView(View):
    def get(self, request, grade_id, term):
        # Get grade, students, subjects (ordered by numbering), and exams
        grade = get_object_or_404(Grade, pk=grade_id)
        students = Student.objects.filter(grade=grade)
        subjects = Subject.objects.filter(grade=grade).order_by("numbering")
        exams = Exam.objects.filter(grade=grade, term=term).order_by("created")

        # Total number of learners in this grade
        num_students = students.count()

        # Preload all performances to reduce DB hits
        all_performances = StudentPerformance.objects.filter(
            exam__in=exams, student__in=students
        )

        # Build a map of (student, exam, subject) → score
        perf_map = {
            (p.student_id, p.exam_id, p.subject_id): p.performance
            for p in all_performances
        }

        reports = []

        # Compute per-student, per-exam totals and averages
        for student in students:
            exam_scores = {}
            exam_totals = {}
            exam_averages = {}

            for exam in exams:
                subject_scores = {}
                total = 0
                count = 0

                for subject in subjects:
                    key = (student.id, exam.id, subject.id)
                    score = perf_map.get(key)
                    if score is not None:
                        subject_scores[subject.id] = score
                        total += score
                        count += 1

                exam_scores[exam.id] = subject_scores
                exam_totals[exam.id] = total
                exam_averages[exam.id] = round(total / count, 2) if count > 0 else 0

            reports.append({
                "student": student,
                "exam_scores": exam_scores,
                "exam_totals": exam_totals,
                "exam_averages": exam_averages,
            })

        # Calculate rank per exam (and include "out of" text)
        for exam in exams:
            ranked = sorted(
                [(r, r["exam_totals"].get(exam.id, 0)) for r in reports],
                key=lambda x: x[1],
                reverse=True,
            )

            for rank, (report, score) in enumerate(ranked, start=1):
                if "exam_ranks" not in report:
                    report["exam_ranks"] = {}
                # Store as "X / N" format
                report["exam_ranks"][exam.id] = f"{rank} out of {num_students}"

        # Fixed or dynamic term dates
        opening_date = "10th January 2025"
        closing_date = "5th April 2025"

        # ✅ Resolve absolute logo path for WeasyPrint
        logo_filename = "Logo.png"
        logo_relative_path = os.path.join("images", logo_filename)

        # Prefer STATIC_ROOT if available (after collectstatic), else STATICFILES_DIRS
        if hasattr(settings, "STATIC_ROOT") and os.path.exists(settings.STATIC_ROOT):
            logo_path = os.path.join(settings.STATIC_ROOT, logo_relative_path)
        elif hasattr(settings, "STATICFILES_DIRS") and settings.STATICFILES_DIRS:
            logo_path = os.path.join(settings.STATICFILES_DIRS[0], logo_relative_path)
        else:
            # Fallback to BASE_DIR/static
            logo_path = os.path.join(settings.BASE_DIR, "static", logo_relative_path)

        logo_uri = f"file://{os.path.abspath(logo_path)}"

        # Context for templates
        context = {
            "school_name": "UNITED MATUNDA ACADEMY",
            "grade": grade,
            "term": term,
            "subjects": subjects,
            "exams": exams,
            "reports": reports,
            "opening_date": opening_date,
            "closing_date": closing_date,
            "logo_path": logo_uri,
        }

        # Render HTML to string
        html_string = render_to_string("term_report_cards.html", context)

        # ✅ Generate PDF with correct static resolution
        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

        # Return downloadable PDF
        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{grade}_Term_{term}_Report_Cards.pdf"'
        return response

class TermExamAnalysis(TemplateView):
    template_name = 'term_analysis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grade_id = self.kwargs.get('grade_id')
        term = self.kwargs.get('term')

        grade = get_object_or_404(Grade, id=grade_id)
        context['grade'] = grade
        context['term'] = term

        # Exams in this grade and term
        exams = Exam.objects.filter(grade=grade, term=term).order_by('created')
        students = Student.objects.filter(grade=grade)
        subjects = Subject.objects.filter(grade=grade)

        context['exams'] = exams
        context['subjects'] = subjects

        # ===== SUBJECT AVERAGES ====+
        subject_averages = {}
        for subject in subjects.order_by('name'):
            teacher_name = subject.teacher.full_name if subject.teacher else "N/A"

            exam_avgs = []
            for exam in exams:
                avg_score = StudentPerformance.objects.filter(
                    exam=exam, subject=subject
                ).aggregate(avg=Avg('performance'))['avg'] or 0
                exam_avgs.append(round(avg_score, 2))
            overall_avg = round(sum(exam_avgs) / len(exams), 2) if exams else 0
            exam_avgs.append(overall_avg)

            subject_averages[subject.name] = {
                "teacher": teacher_name,
                "averages": exam_avgs
            }
        context["subject_averages"] = subject_averages

        # ===== TOP/BOTTOM SUBJECTS =====
        # Sort subjects by their overall average (last value in averages list)
        sorted_subjects = sorted(
            subject_averages.items(),
            key=lambda x: x[1]["averages"][-1],  # sort by overall average
            reverse=True
        )

        context["top_subjects"] = sorted_subjects[:3]
        context["subjects_needing_improvement"] = sorted_subjects[-3:]

        # ===== LEARNER PERFORMANCE =====
        student_performance_data = []
        for student in students:
            exam_scores = []
            for exam in exams:
                avg_score = StudentPerformance.objects.filter(
                    exam=exam, student=student
                ).aggregate(avg=Avg('performance'))['avg'] or 0
                exam_scores.append(round(avg_score, 2))

            average_score = round(sum(exam_scores) / len(exams), 2) if exams else 0
            improvement = exam_scores[-1] - exam_scores[0] if len(exam_scores) > 1 else 0

            student_performance_data.append({
                'student': student,
                'exam_scores': exam_scores,
                'average_score': average_score,
                'improvement': improvement,
            })

        # Sort by improvement (descending)
        student_performance_data.sort(key=lambda x: x['improvement'], reverse=True)
        context['student_performance_data'] = student_performance_data

        # ===== CONSISTENT IMPROVEMENT / DECLINE =====
        consistently_improving = []
        declining_students = []
        for data in student_performance_data:
            scores = data['exam_scores']
            if len(scores) > 1:
                if all(x < y for x, y in zip(scores, scores[1:])):
                    consistently_improving.append(data['student'])
                elif all(x > y for x, y in zip(scores, scores[1:])):
                    declining_students.append(data['student'])

        context['consistently_improving'] = consistently_improving
        context['declining_students'] = declining_students

        # ===== GRADE-LEVEL TRENDS =====
        grade_trends = []
        for exam in exams:
            avg_score = StudentPerformance.objects.filter(exam=exam).aggregate(avg=Avg('performance'))['avg'] or 0
            grade_trends.append(round(avg_score, 2))
        context['grade_trends'] = grade_trends

        return context


class GenerateClassReportCardsView(View):

    def get(self, request, exam_id):

        exam = get_object_or_404(Exam, pk=exam_id)
        grade = exam.grade

        students = Student.objects.filter(grade=grade).order_by("first_name")
        subjects = Subject.objects.filter(grade=grade).order_by("numbering")

        # -------------------------------------------------
        # Fetch all performances once
        # -------------------------------------------------
        performances = StudentPerformance.objects.filter(
            exam=exam,
            student__in=students,
            subject__in=subjects
        )

        # Map (student_id, subject_id) → score
        perf_map = {
            (p.student_id, p.subject_id): p.performance
            for p in performances
        }

        # -------------------------------------------------
        # Compute student totals and build reports
        # -------------------------------------------------
        student_totals = {}
        reports = []

        for student in students:

            subject_scores = {}
            total = 0
            count = 0

            for subject in subjects:

                score = perf_map.get((student.id, subject.id))

                if score is not None:
                    subject_scores[subject.id] = score
                    total += score
                    count += 1
                else:
                    subject_scores[subject.id] = None

            average = round(total / count, 2) if count else 0

            student_totals[student.id] = total

            reports.append({
                "student": student,
                "scores": subject_scores,
                "total": total,
                "average": average,
            })

        # -------------------------------------------------
        # Dense Ranking Algorithm (Tie-safe ranking)
        # -------------------------------------------------

        sorted_totals = sorted(
            student_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )

        rank_lookup = {}

        rank = 1
        prev_score = None
        position_counter = 0

        for student_id, total in sorted_totals:

            position_counter += 1

            if prev_score is not None and total < prev_score:
                rank = position_counter

            rank_lookup[student_id] = rank
            prev_score = total

        # -------------------------------------------------
        # Attach metadata to reports
        # -------------------------------------------------

        total_students = students.count()

        for report in reports:

            sid = report["student"].id

            report["rank"] = rank_lookup.get(sid)
            report["total_students"] = total_students
            report["term_total"] = report["total"]
            report["term_average"] = report["average"]

        # -------------------------------------------------
        # Subject averages (efficient aggregation)
        # -------------------------------------------------

        subject_averages = {
            subject.id: performances.filter(subject=subject)
            .aggregate(avg=Avg("performance"))["avg"] or 0
            for subject in subjects
        }

        # -------------------------------------------------
        # Class mean score
        # -------------------------------------------------

        class_mean = performances.aggregate(
            avg=Avg("performance")
        )["avg"] or 0

        # -------------------------------------------------
        # Resolve logo path safely
        # -------------------------------------------------

        logo_filename = "Logo.png"
        logo_relative_path = os.path.join("images", logo_filename)

        logo_path = None

        if hasattr(settings, "STATIC_ROOT") and settings.STATIC_ROOT:
            candidate = os.path.join(settings.STATIC_ROOT, logo_relative_path)
            if os.path.exists(candidate):
                logo_path = candidate

        if not logo_path and settings.STATICFILES_DIRS:
            candidate = os.path.join(settings.STATICFILES_DIRS[0], logo_relative_path)
            if os.path.exists(candidate):
                logo_path = candidate

        if not logo_path:
            logo_path = os.path.join(settings.BASE_DIR, "static", logo_relative_path)

        logo_uri = f"file://{os.path.abspath(logo_path)}"

        # -------------------------------------------------
        # Render PDF
        # -------------------------------------------------

        html_string = render_to_string(
            "single_exam_report_cards.html",
            {
                "exam": exam,
                "grade": grade,
                "subjects": subjects,
                "reports": reports,
                "subject_averages": subject_averages,
                "class_mean": round(class_mean, 2),
                "logo_path": logo_uri,
            }
        )

        pdf_file = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")

        response["Content-Disposition"] = (
            f'attachment; filename="{exam.exam_name}_{grade}_Class_Report_Cards.pdf"'
        )

        return response