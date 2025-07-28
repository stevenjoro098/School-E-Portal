from django.db import models

# Create your models here.
class Grade(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.name}"

class Subject(models.Model):
    #grade = models.ForeignKey(Grade, on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.name}"

