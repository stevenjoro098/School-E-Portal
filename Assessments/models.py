from django.db import models
from Subjects.models import Subject, Grade
from django.contrib.auth.models import User
# Create your models here.


class Assessment(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User,  on_delete=models.CASCADE, blank=True, null=True)
    grade = models.ForeignKey(Grade, related_name='grade_assessments', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.CharField(max_length=250)
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    done = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f"{self.title} ({self.subject})"

    def publish(self):
        self.is_published = True
        self.save()


class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    marks = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.text[:60]

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class StudentAnswer(models.Model):
    student = models.CharField(max_length=250)#ForeignKey(StudentProfile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def is_correct(self):
        return self.selected_choice.is_correct

class AssessmentResult(models.Model):
    student = models.CharField(max_length=250)
    assessment = models.ForeignKey(Assessment,  on_delete=models.CASCADE)
    total_score = models.PositiveIntegerField()
    answers = models.JSONField(null=True, blank=True)
    #max_score = models.PositiveIntegerField(blank=True)
    completed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{ self.student } - { self.assessment.title }"
