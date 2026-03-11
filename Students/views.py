import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView
from django.contrib import messages

from Students.models import Student, ReamPaperRecords
from Subjects.models import Grade


# Create your views here.
class StudentCreateView(CreateView):
    model = Student
    template_name = 'register_student.html'
    fields = ['first_name','second_name','third_name','grade','gender','image','residence','favorite_sport','hobbies']
    def get_success_url(self):
        return reverse('student_details_view', kwargs={'pk': self.object.pk})

class StudentDetailView(DetailView):
    model = Student
    template_name = 'student_detail_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students_assessments'] = self.object.student_assessments.all()
        return context

class UpdateStudent(UpdateView):
    model = Student
    template_name = 'register_student.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse('student_details_view', kwargs={'pk': self.object.pk})

class SearchStudentPage(TemplateView):
    template_name = 'search_student.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assessment_id'] = self.kwargs['assessment_id']
        grades = list(Grade.objects.values("id", "name"))
        context['grades_json'] = json.dumps(grades)   # make it valid JSON
        return context


class StudentsByGradeView(View):
    def get(self, request, grade_id):
        students = Student.objects.filter(grade_id=grade_id).values("id", "first_name", "second_name")
        return JsonResponse(list(students), safe=False)

class StudentsList(TemplateView, View):
    model = Student
    template_name = 'student_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grades = list(Grade.objects.values("id", "name"))
        context['grades_json'] = json.dumps(grades)   # make it valid JSON
        return context


# ===================== CLASS MANAGEMENT =====================================
class ClassManagement(TemplateView, View):
    template_name = 'classmngt/class_mngt.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.grade =  get_object_or_404(Grade, id=kwargs['grade_id'])
        context['grade'] = self.grade
        context["students"] = Student.objects.filter(grade=self.grade)
        return context

from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from Students.models import Student, ReamPaperRecords


class EditStudentReam(TemplateView):
    template_name = 'classmngt/update_student_ream.html'

    def get(self, request, *args, **kwargs):
        student = get_object_or_404(Student, id=self.kwargs['student_id'])

        ream_status, created = ReamPaperRecords.objects.get_or_create(
            student=student
        )

        return self.render_to_response({
            'student': student,
            'ream_status': ream_status
        })


    def post(self, request, *args, **kwargs):

        student = get_object_or_404(Student, id=self.kwargs['student_id'])

        ream_status, created = ReamPaperRecords.objects.get_or_create(
            student=student
        )

        first_term = "first_term" in request.POST
        second_term = "second_term" in request.POST

        ream_status.first_term = first_term
        ream_status.second_term = second_term
        ream_status.save()

        messages.success(request, "Ream paper status updated successfully.")

        return redirect(request.path)