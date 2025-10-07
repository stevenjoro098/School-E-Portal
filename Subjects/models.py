from django.db import models

# Create your models here.
class Grade(models.Model):
    name = models.CharField(max_length=250)

    class Meta:
        ordering = ('-name',)
    def __str__(self):
        return f"{self.name}"

class Subject(models.Model):
    numbering = models.PositiveIntegerField(blank=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='grade_subjects',blank=True)
    name = models.CharField(max_length=250)

    class Meta:
        ordering = ('numbering',)

    def __str__(self):
        return f"{self.name}"

