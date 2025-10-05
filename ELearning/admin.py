from django.contrib import admin

from ELearning.models import Subject, Strand, SubStrand, LearningOutcome, Note, ImageResource

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