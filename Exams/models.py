from django.db import models

from Students.models import Student
from Subjects.models import Grade, Subject

terms = (
    ('Term 1','Term 1'),
    ('Term 2','Term 2'),
    ('Term 3','Term 3'),
)
# Create your models here.
class Exam(models.Model):
    exam_name = models.CharField(max_length=250)
    term = models.CharField(max_length=250, choices=terms)
    created = models.DateField(auto_now_add=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='grade_exam')

    def __str__(self):
        return f"{self.exam_name} - {self.grade}"

class ExamSubject(models.Model):
    exam = models.ForeignKey(Exam, related_name='exam_subjects', on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='exam_grade_subjects', blank=True, null=True)
    exam_subject = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.exam_subject} - {self.exam}"

class StudentPerformance(models.Model):
    student = models.ForeignKey(Student, related_name='student_performance', on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_performance')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    performance = models.PositiveIntegerField()
    created = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject', 'exam')

    def __str__(self):
        return f"{self.student} - {self.exam.exam_name} - {self.subject}: {self.performance}"
