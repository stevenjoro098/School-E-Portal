import os
from weasyprint import HTML, CSS
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from django.shortcuts import get_object_or_404
from weasyprint import HTML
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, ListView, DetailView, DeleteView, UpdateView
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from Students.models import Student
from .forms import *
from django.http import JsonResponse
from .models import Assessment, StudentAnswer, Question, Choice, AssessmentResult
import json

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def Home(request):
    #user_profile = request.user.studentprofile
    assessments = Assessment.objects.filter(is_published=True)
    return render(request, 'assessment_home_page.html', {'assessments': assessments})


class Dashboard(LoginRequiredMixin, ListView):
    template_name = 'dashboard.html'
    #login_url = '/login/'  # optional: where to redirect if not logged in
    #redirect_field_name = 'next'  # optional
    context_object_name = 'teacher_assessment_list'
    def get_queryset(self):
        return Assessment.objects.filter(user=self.request.user)


class AssessmentCreate(CreateView):
    template_name = 'assessment_form.html'
    model = Assessment
    form_class = AssessmentForm

    def form_valid(self, form):
        form.instance.user = self.request.user  # Attach the logged-in user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard')

class AssessmentPublish(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        assessment = get_object_or_404(Assessment, pk=pk, user=request.user)
        assessment.publish()
        return redirect('dashboard')  # Adjust the redirect URL

class AssessmentAnalysis(LoginRequiredMixin, ListView):
    model = AssessmentResult
    template_name = 'assessment_analysis.html'
    context_object_name = 'assessment_result_list'

    def get_queryset(self):
        self.assessment = get_object_or_404(Assessment, pk=self.kwargs['assessment_id'])
        return AssessmentResult.objects.filter(assessment=self.assessment)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assessment_id'] = self.kwargs['assessment_id']
        context['assessment'] = self.assessment
        return context

class AssessmentEditView(LoginRequiredMixin, UpdateView):
    model = Assessment
    template_name = 'assessment_form.html'  # You can reuse the create template if you like
    fields = ['title', 'subject', 'grade', 'teacher', 'scheduled_date', 'duration_minutes', 'is_published']


    def get_success_url(self):
        return reverse_lazy('dashboard')

class AssessmentDelete(LoginRequiredMixin, DeleteView):
    model = Assessment
    template_name = 'assessment_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

class QuestionCreateView(CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'questions_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=self.kwargs['assessment_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ChoiceFormSet(self.request.POST)
        else:
            context['formset'] = ChoiceFormSet()
        context['assessment'] = self.assessment
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            form.instance.assessment = self.assessment
            self.object = form.save()

            choices = formset.save(commit=False)
            for choice in choices:
                choice.question = self.object
                choice.save()

            return redirect('create_questions', assessment_id=self.assessment.id)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class QuestionUpdateView(UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'edit_questions_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ChoiceFormSetDynamic = inlineformset_factory(
            Question,
            Choice,
            fields=('text', 'is_correct'),
            extra=0,
            can_delete=True
        )

        if self.request.POST:
            context['formset'] = ChoiceFormSetDynamic(self.request.POST, instance=self.object)
        else:
            context['formset'] = ChoiceFormSetDynamic(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect('create_questions', assessment_id=self.object.assessment.pk)

        # ❗ Add debugging for errors
        print("FORMSET ERRORS:")
        print(formset.errors)
        print("FORMSET CLEANED DATA:")
        print(formset.cleaned_data)
        return self.render_to_response(self.get_context_data(form=form))


def take_assessment(request, assessment_id, student_id):
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    questions = assessment.questions.prefetch_related('choices').all()
    student = get_object_or_404(Student, id=student_id)
    taken = AssessmentResult.objects.filter(assessment_id=assessment_id, student=student).exists()
    if taken:
        assessment_result = AssessmentResult.objects.get(assessment=assessment, student=student)
    question_data = []
    for q in questions:
        choices = [{'id': c.id, 'text': c.text} for c in q.choices.all()]
        question_data.append({'id': q.id, 'text': q.text, 'choices': choices})

    return render(request, 'take_assessment.html', {
        'result': assessment_result,
        "taken": taken,
        'student': student,
        'assessment': assessment,
        'questions_json': json.dumps(question_data)
    })

def check_if_taken(request, assessment_id):
    name = request.GET.get('name')
    print(name)
    taken = AssessmentResult.objects.filter(assessment_id=assessment_id, student__iexact=name).exists()
    return JsonResponse({'taken': taken})


#@login_required
class SubmitAssessmentView(View):
    def post(self, request, assessment_id):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        answers = data.get('answers', [])
        student_id = data.get('student_id')
        if not student_id:
            return JsonResponse({"error": "Missing student name"}, status=400)

        assessment = get_object_or_404(Assessment, id=assessment_id)
        questions = assessment.questions.all()

        correct = 0
        total = questions.count()
        answer_map = {}

        for i, question in enumerate(questions):
            try:
                selected_id = answers[i]
                selected = Choice.objects.get(id=selected_id)
                answer_map[str(question.id)] = selected_id
                if selected.is_correct:
                    correct += 1
            except (IndexError, Choice.DoesNotExist):
                answer_map[str(question.id)] = None  # No answer

        percentage = round((correct / total) * 100, 2) if total > 0 else 0
        student = get_object_or_404(Student, id=student_id)
        result = AssessmentResult.objects.create(
            student=student,
            assessment=assessment,
            total_score=correct,
            answers=answer_map  # Save answers
        )

        return JsonResponse({
            "score": correct,
            "max_score": total,
            "percentage": percentage,
            "redirect_url": f"/assessment/result/{result.id}/"
        })

class AssessmentResultView(DetailView):
    model = AssessmentResult
    template_name = "results.html"
    context_object_name = "result"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = self.get_object()
        assessment = result.assessment
        questions = assessment.questions.all()
        answers = result.answers or {}

        data = []
        correct_count = 0

        for q in questions:
            selected_choice_id = answers.get(str(q.id))
            selected_choice = Choice.objects.filter(id=selected_choice_id).first()
            correct_choice = q.choices.filter(is_correct=True).first()

            is_correct = (
                selected_choice_id == correct_choice.id
                if (selected_choice and correct_choice) else False
            )
            if is_correct:
                correct_count += 1

            data.append({
                "question": q.text,
                "selected": selected_choice.text if selected_choice else "No answer",
                "correct": correct_choice.text if correct_choice else "N/A",
                "is_correct": is_correct,
            })

        total = questions.count()
        percentage = round((correct_count / total) * 100, 2) if total else 0

        context.update({
            "assessment": assessment,
            "student_name": result.student,  # 👈 Use student name from AssessmentResult
            "questions_data": data,
            "correct_count": correct_count,
            "total": total,
            "percentage": percentage,
        })
        return context


def download_result_pdf(request, result_id):
    result = get_object_or_404(AssessmentResult, id=result_id)
    assessment = result.assessment
    questions = assessment.questions.all()

    data = []
    correct_count = 0

    for q in questions:
        selected_choice_id = result.answers.get(str(q.id))
        selected_choice = Choice.objects.filter(id=selected_choice_id).first()
        correct_choice = q.choices.filter(is_correct=True).first()
        is_correct = selected_choice_id == correct_choice.id if selected_choice and correct_choice else False
        if is_correct:
            correct_count += 1

        data.append({
            "question": q.text,
            "selected": selected_choice.text if selected_choice else "No answer",
            "correct": correct_choice.text if correct_choice else "N/A",
            "is_correct": is_correct,
        })

    total = len(questions)
    percentage = round((correct_count / total) * 100, 2) if total else 0

    context = {
        "assessment": assessment,
        "result": result,
        "questions_data": data,
        "correct_count": correct_count,
        "total": total,
        "percentage": percentage,
        "student_name": result.student,
        "student_grade": assessment.grade.name,
        "now": timezone.now()
    }

    # Load template and render to HTML
    template = get_template("pdf/result_pdf.html")
    html_content = template.render(context)

    # Path to your custom font (ensure it exists)
    font_path = os.path.join(settings.BASE_DIR, 'static/fonts/century_gothic.ttf')
    css = CSS(string=f"""
        @font-face {{
            font-family: 'Century Gothic';
            src: url('file://{font_path}') format('truetype');
        }}
        body {{
            font-family: 'Century Gothic', sans-serif;
            font-size: 13px;
            padding: 30px;
        }}
        .header {{
            text-align: center;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        .score {{
            text-align: center;
            font-size: 16px;
            background-color: #f0f8ff;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
        }}
        .question {{
            margin-bottom: 15px;
            padding: 10px;
            border-bottom: 1px solid #ccc;
        }}
        .correct {{
            color: green;
        }}
        .wrong {{
            color: red;
        }}
    """)

    pdf_file = HTML(string=html_content).write_pdf(stylesheets=[css])
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{ result.student } -- { result.assessment.title }_result_.pdf"'
    return response

def questions_list_pdf(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    questions = Question.objects.filter(assessment=assessment)

    context = {
        'questions': questions,
        'assessment': assessment
    }
    html_string = render_to_string("pdf/questions_list_pdf.html", context)
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="assessment_questions_{assessment.id}.pdf"'
    return response

def generate_assessment_summary_pdf(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    results = AssessmentResult.objects.filter(assessment=assessment)

    learners_data = []
    for result in results:
        questions = assessment.questions.all()
        total_questions = questions.count()
        correct_count = 0

        for q in questions:
            selected_id = result.answers.get(str(q.id))
            correct_choice = q.choices.filter(is_correct=True).first()
            if selected_id and correct_choice and str(correct_choice.id) == str(selected_id):
                correct_count += 1

        percentage = round((correct_count / total_questions) * 100, 2) if total_questions else 0

        learners_data.append({
            "name": str(result.student).title(),
            "grade": getattr(result, "grade", "N/A"),
            "correct": correct_count,
            "total": total_questions,
            "percentage": percentage,
        })

    # Sort and rank learners
    ranked_learners = sorted(learners_data, key=lambda x: x["percentage"], reverse=True)
    for index, learner in enumerate(ranked_learners, start=1):
        learner["rank"] = index

    percentages = [l["percentage"] for l in ranked_learners]
    total_learners = len(ranked_learners)
    average_score = round(sum(percentages) / total_learners, 2) if total_learners else 0
    highest_score = max(percentages) if percentages else 0
    lowest_score = min(percentages) if percentages else 0

    context = {
        "assessment": assessment,
        "now": timezone.now(),
        "total_learners": total_learners,
        "average_score": average_score,
        "highest_score": highest_score,
        "lowest_score": lowest_score,
        "ranked_learners": ranked_learners,
    }

    html_string = render_to_string("pdf/assessment_analysis_pdf.html", context)
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="assessment_summary_{assessment.id}.pdf"'
    return response

class QuestionsListView(ListView):
    template_name = 'view_questions_list.html'
    model = Question
    context_object_name = 'questions_list'


    def get_queryset(self):
        self.assessment = get_object_or_404(Assessment, id=self.kwargs['assessment_id'])
        return Question.objects.filter(assessment=self.assessment)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assessment'] = self.assessment
        return context