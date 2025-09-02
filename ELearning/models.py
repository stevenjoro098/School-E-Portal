from django.db import models
from django.contrib.auth.models import User

from Subjects.models import Grade


class Subject(models.Model):
    name = models.CharField(max_length=100)
    grade = models.ForeignKey(Grade, related_name='grade_subject', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

class Strand(models.Model):
    subject = models.ForeignKey(Subject, related_name='strands', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class SubStrand(models.Model):
    strand = models.ForeignKey(Strand, related_name='substrands', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class LearningOutcome(models.Model):
    substrand = models.ForeignKey(SubStrand, related_name='learning_outcomes', on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return self.description[:50]

class Activity(models.Model):
    outcome = models.ForeignKey(LearningOutcome, related_name='activities', on_delete=models.CASCADE)
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