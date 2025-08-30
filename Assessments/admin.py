from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['title',
                    'subject',
                    'grade',
                    'teacher',
                    'scheduled_date',
                    'duration_minutes',
                    'is_published',
                    'done']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['assessment','text','marks']

@admin.register(Choice)
class ChoicesAdmin(admin.ModelAdmin):
    list_display = ['question','text','is_correct']


@admin.register(StudentAnswer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['student','question','selected_choice']

@admin.register(AssessmentResult)
class AssessmentResult(admin.ModelAdmin):
    list_display = ['student','assessment','total_score','completed_on']
