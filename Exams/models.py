from django.db import models

from Students.models import Student
from Subjects.models import Grade

grades = (
    ('PP1','PP1',),
    ('PP2','PP2'),
    ('Grade 1', 'Grade 1'),
    ('Grade 2', 'Grade 2'),
    ('Grade 3', 'Grade 3'),
    ('Grade 4', 'Grade 4'),
    ('Grade 5', 'Grade 5'),
    ('Grade 6', 'Grade 6'),
    ('Grade 7', 'Grade 7'),
    ('Grade 8', 'Grade 8'),
    ('Grade 9', 'Grade 9'),
)

# Create your models here.
class Exam(models.Model):
    exam_name = models.CharField(max_length=250)
    created = models.DateField(auto_now_add=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='grade_exam')

    def __str__(self):
        return f"{self.exam_name} - {self.grade}"

class ExamSubject(models.Model):
    exam = models.ForeignKey(Exam, related_name='exam_subjects', on_delete=models.CASCADE)
    exam_subject = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.exam_subject} - {self.exam}"

class StudentPerformance(models.Model):
    student = models.ForeignKey(Student, related_name='student_performance', on_delete=models.CASCADE)
    exam_subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_performance')
    created = models.DateField(auto_now_add=True)
    performance = models.PositiveIntegerField()

    class Meta:
        unique_together = ('student', 'exam_subject', 'exam')

