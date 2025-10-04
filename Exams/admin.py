from django.contrib import admin

from .models import Exam, Subject, StudentPerformance

# Register your models here.
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['exam_name','created','grade']
    list_filter = ['grade','created']


class SubjectByGradeFilter(admin.SimpleListFilter):
    title = "Subject"
    parameter_name = "subject"

    def lookups(self, request, model_admin):
        exam_id = request.GET.get("exam__id__exact")
        if exam_id:
            exam = Exam.objects.filter(id=exam_id).first()
            if exam and exam.grade:
                return [(s.id, s.name) for s in exam.grade.grade_subjects.all()]
        # fallback: show all subjects
        return [(s.id, s.name) for s in Subject.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(subject_id=self.value())
        return queryset

@admin.register(StudentPerformance)
class StudentPerformanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'subject', 'performance', 'created']
    list_filter = ['exam', SubjectByGradeFilter]