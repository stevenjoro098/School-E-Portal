from django.contrib import admin

from .models import Exam, Subject, StudentPerformance

# Register your models here.
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['exam_name','created','grade']
    list_filter = ['grade','created']


# @admin.register(Subject)
# class ExamSubjectAdmin(admin.ModelAdmin):
#     list_display = ['exam','subject']
#     list_filter = ['exam']

@admin.register(StudentPerformance)
class StudentPerformance(admin.ModelAdmin):
    list_display = ['student', 'exam','subject','performance', 'created']
    list_filter = ['exam','subject']