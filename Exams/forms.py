from django import forms
from django.forms import modelformset_factory
from .models import StudentPerformance

class StudentPerformanceForm(forms.ModelForm):
    class Meta:
        model = StudentPerformance
        fields = ['performance']
