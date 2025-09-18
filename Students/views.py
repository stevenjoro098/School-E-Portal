import json

from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView

from Students.models import Student
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