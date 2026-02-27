from django import forms
from Subjects.models import Subject
from Students.models import Teachers

# forms.py

class TimetableCellForm(forms.Form):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        required=False
    )
    teacher = forms.ModelChoiceField(
        queryset=Teachers.objects.none(),
        required=False
    )

    def __init__(self, *args, grade=None, **kwargs):
        super().__init__(*args, **kwargs)

        if grade:
            # 🔹 Filter subjects by grade
            self.fields["subject"].queryset = Subject.objects.filter(
                grade=grade
            )

            # 🔹 Optional: Filter teachers teaching this grade
            self.fields["teacher"].queryset = Teachers.objects.all()