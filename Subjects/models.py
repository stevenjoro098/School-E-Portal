from django.db import models

class Grade(models.Model):
    name = models.CharField(max_length=250)

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return f"{self.name}"


class Subject(models.Model):
    numbering = models.PositiveIntegerField(blank=True)
    name = models.CharField(max_length=250)
    grade = models.ForeignKey('Subjects.Grade', on_delete=models.CASCADE, related_name='grade_subjects', blank=True)
    teacher = models.ForeignKey('Students.Teachers', on_delete=models.CASCADE, related_name='teacher_subjects', blank=True, null=True)

    class Meta:
        ordering = ('numbering',)

    def __str__(self):
        return f"{self.name}"
