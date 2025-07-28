# forms.py
from django import forms
from django.forms.models import inlineformset_factory
from .models import Question, Choice
from .models import Assessment

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']

ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    fields=['text', 'is_correct'],
    extra=4,  # Number of choice inputs shown
    can_delete=True
)


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['title', 'subject', 'grade', 'teacher', 'scheduled_date', 'duration_minutes']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
