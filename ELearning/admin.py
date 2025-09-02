from django.contrib import admin

from ELearning.models import Subject, Strand, SubStrand, LearningOutcome, Note, ImageResource


# Register your models here.
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name','grade']

@admin.register(Strand)
class StrandAdmin(admin.ModelAdmin):
    list_display = ['name','subject',]

@admin.register(SubStrand)
class SubStrandAdmin(admin.ModelAdmin):
    list_display = ['name','strand',]


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['substrand']

@admin.register(ImageResource)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['substrand']

@admin.register(LearningOutcome)
class LearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ['substrand','description']