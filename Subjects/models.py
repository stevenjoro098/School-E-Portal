from django.db import models

from Students.models import Teachers


class Grade(models.Model):
    name = models.CharField(max_length=250)
    class_teacher = models.OneToOneField(Teachers, related_name='class_teacher', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return f"{self.name}"


class Subject(models.Model):
    numbering = models.PositiveIntegerField(blank=True, null=True)
    name = models.CharField(max_length=250)
    grade = models.ForeignKey('Subjects.Grade', on_delete=models.SET_NULL, related_name='grade_subjects', blank=True, null=True)
    teacher = models.ForeignKey('Students.Teachers', on_delete=models.SET_NULL, related_name='teacher_subjects', blank=True, null=True)

    class Meta:
        ordering = ('numbering',)

    def __str__(self):
        return f"{self.name}"
