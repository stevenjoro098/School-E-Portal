from django.db import models

from Subjects.models import Grade

# Create your models here.
gender = (
    ('Boy','Boy'),
    ('Girl','Girl')
)
class Student(models.Model):
    first_name = models.CharField(max_length=200)
    second_name = models.CharField(max_length=200)
    third_name = models.CharField(max_length=200, blank=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, blank=True, null=True)
    gender = models.CharField(choices=gender, max_length=200)
    image = models.ImageField(upload_to='students', blank=True)
    residence = models.CharField(max_length=200)
    favorite_sport = models.CharField(max_length=200, blank=True)
    hobbies = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.second_name} - {self.grade}"