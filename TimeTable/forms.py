from django import forms
from Subjects.models import Subject
from Students.models import Teachers

class TimetableCellForm(forms.Form):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        required=False
    )
    teacher = forms.ModelChoiceField(
        queryset=Teachers.objects.all(),
        required=False
    )