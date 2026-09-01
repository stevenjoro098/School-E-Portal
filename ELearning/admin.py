from django.contrib import admin
from .models import VideosResource, SubStrandCoverage, VideoResource, ImageGeneralResource, FileResource
from ELearning.models import Subject, Strand, SubStrand, LearningOutcome, Note, ImageResource


@admin.register(SubStrandCoverage)
class SubstrandCoverageAdmin(admin.ModelAdmin):
    list_display = ['substrand','status']

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

@admin.register(VideosResource)
class VideosResources(admin.ModelAdmin):
    list_display = ['title']

@admin.register(ImageGeneralResource)
class ImageResourceAdmin(admin.ModelAdmin):
    list_display = ['image_title']

@admin.register(FileResource)
class FileResource(admin.ModelAdmin):
    list_display = ['file_title']