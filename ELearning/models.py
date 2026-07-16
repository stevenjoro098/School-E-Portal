from django.db import models
from django.contrib.auth.models import User

from Subjects.models import Grade, Subject


class Strand(models.Model):
    subject = models.ForeignKey(Subject, related_name='subject_strands', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class SubStrand(models.Model):
    strand = models.ForeignKey(Strand, related_name='substrands', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class LearningOutcome(models.Model):
    substrand = models.ForeignKey(SubStrand, related_name='learning_outcomes', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.description[:50]

class Activity(models.Model):
    outcome = models.ForeignKey(LearningOutcome, related_name='activities', on_delete=models.SET_NULL, null=True, blank=True)
    activity_type = models.CharField(max_length=50, choices=[
        ('video', 'Video'),
        ('quiz', 'Quiz'),
        ('simulation', 'Simulation'),
        ('practical', 'Practical'),
        ('image', 'Image'),
    ])
    resource_link = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='activities/images/', blank=True, null=True)

    def __str__(self):
        return f"{self.activity_type} - {self.resource_link}"
class SubStrandCoverage(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    #grade = models.ForeignKey(Grade,on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
    substrand = models.ForeignKey(SubStrand,on_delete=models.CASCADE)
    term = models.CharField(max_length=200)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='not_started')
    started_on = models.DateField(null=True, blank=True)
    completed_on = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.substrand} - {self.grade} - {self.status}"


class Assessment(models.Model):
    outcome = models.ForeignKey(LearningOutcome, related_name='assessments', on_delete=models.CASCADE)
    assessment_type = models.CharField(max_length=50, choices=[
        ('quiz', 'Quiz'),
        ('project', 'Project'),
        ('portfolio', 'Portfolio'),
    ])
    rubric = models.JSONField(help_text="CBC rubric details")

    def __str__(self):
        return f"{self.assessment_type} for {self.outcome}"

class SubStrandNote(models.Model):
    strand = models.ForeignKey(Strand, related_name='notes', on_delete=models.CASCADE)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Note {self.id} for Strand {self.strand_id}"

class Note(models.Model):
    substrand = models.ForeignKey(SubStrand, on_delete=models.CASCADE, related_name="notes")
    content = models.TextField()

class ImageResource(models.Model):
    substrand = models.ForeignKey(SubStrand, on_delete=models.CASCADE, related_name="images")
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='substrand_images/')

class VideoResource(models.Model):
    substrand = models.ForeignKey(SubStrand, on_delete=models.CASCADE, related_name="videos")
    url = models.URLField()

class VideosResource(models.Model):
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    video = models.FileField(upload_to='videos/')
    #uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title