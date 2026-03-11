from django.db import models



# Create your models here.
gender = (
    ('Boy','Boy'),
    ('Girl','Girl')
)
class Student(models.Model):
    first_name = models.CharField(max_length=200)
    second_name = models.CharField(max_length=200)
    third_name = models.CharField(max_length=200, blank=True)
    grade = models.ForeignKey('Subjects.Grade', on_delete=models.SET_NULL, blank=True, null=True)
    gender = models.CharField(choices=gender, max_length=200)
    image = models.ImageField(upload_to='students', default='default_profile_image.png', blank=True)
    residence = models.CharField(max_length=200, blank=True)
    favorite_sport = models.CharField(max_length=200, blank=True)
    hobbies = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.second_name} - {self.grade}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.second_name} {self.third_name}".strip()

GENDER = (
    ("Female","Female"),
    ('Male','Male'),
)

class Teachers(models.Model):
    first_name = models.CharField(max_length=200)
    second_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=200, choices=GENDER)
    code_number = models.PositiveIntegerField(blank=True, null=True)
    telephone = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.second_name}"

    @property
    def full_name(self):
        return f'{self.first_name} {self.second_name}'.strip()


class ReamPaperRecords(models.Model):
    student = models.ForeignKey(Student, related_name='student_ream_papers', on_delete=models.SET_NULL, blank=True, null=True)
    first_term = models.BooleanField(default=False)
    second_term = models.BooleanField(default=False)
    used_up = models.BooleanField(default=False)

    def __str__(self):
        return f"{ self.student } - { self.first_term } - { self.second_term }"