from django.contrib import admin

from ELearning.models import Subject, Strand


# Register your models here.
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name','grade']

@admin.register(Strand)
class StrandAdmin(admin.ModelAdmin):
    list_display = ['subject','name']
