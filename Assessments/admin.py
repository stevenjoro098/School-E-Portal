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

@admin.register(AssessmentResult)
class AssessmentResultsAdmin(admin.ModelAdmin):
    list_display = ['student',
                    'assessment',
                    'total_score',
                    'percentage',
                    'total_questions',
                    'completed_on'
                    ]
    list_filter = ['assessment']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['assessment','text','marks']

@admin.register(Choice)
class ChoicesAdmin(admin.ModelAdmin):
    list_display = ['question','text','is_correct']
    list_filter = ['question']


@admin.register(StudentAnswer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['student','question','selected_choice']

