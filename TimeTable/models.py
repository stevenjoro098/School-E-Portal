from django.db import models
from Students.models import Teachers
from Subjects.models import Subject, Grade

class Day(models.Model):
    day = models.CharField(max_length=200, unique=True)
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.day

class TimetableSlot(models.Model):
    grade = models.ForeignKey(Grade, related_name='grade_timetable', on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    teacher = models.ForeignKey(Teachers, related_name='teacher_lessons', null=True, blank=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(Subject, related_name='timetable_subject', null=True, blank=True, on_delete=models.SET_NULL)
    label = models.CharField(max_length=200, blank=True)
    day = models.ForeignKey(Day, related_name='day_time_slots', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Auto-generate label from subject
        if self.subject:
            self.label = str(self.subject.name)  # uses Subject.__str__()
        else:
            self.label = ""

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.grade} - {self.start_time} - {self.end_time} - {self.label} - {self.day}"


