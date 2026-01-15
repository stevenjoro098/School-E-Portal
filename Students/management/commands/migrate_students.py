from django.core.management.base import BaseCommand
from Students.models import Student
from Subjects.models import Grade
class Command(BaseCommand):
    help = "Promotes all students from one grade to another"

    def add_arguments(self, parser):
        parser.add_argument('initial_grade', type=str, help="Current grade of students (e.g., 'Grade 1')")
        parser.add_argument('next_grade', type=str, help="New grade to promote students to (e.g., 'Grade 2')")

    def handle(self, *args, **kwargs):
        initial_grade_name = kwargs['initial_grade']
        next_grade_name = kwargs['next_grade']

        try:
            initial_grade = Grade.objects.get(name=initial_grade_name)
            next_grade = Grade.objects.get(name=next_grade_name)
        except Grade.DoesNotExist:
            self.stdout.write(self.style.ERROR("One or both grades do not exist."))
            return

        updated_count = Student.objects.filter(grade=initial_grade).update(grade=next_grade)

        if updated_count > 0:
            self.stdout.write(self.style.SUCCESS(f"{updated_count} students moved from {initial_grade_name} to {next_grade_name}."))
        else:
            self.stdout.write(self.style.WARNING(f"No students found in {initial_grade_name}."))
