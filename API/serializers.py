from rest_framework import serializers

from Laboratory.models import LabEquipment
from Students.models import Student, Teachers
from Subjects.models import Subject, Grade
from Exams.models import Exam
from Library.models import Book, IssuedBooks

# ================ Student List =========================
class StudentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['first_name','second_name',
                  'third_name','grade',
                  'gender','image',
                  'residence']

class TeacherSerializer(serializers.ModelSerializer):
    model = Teachers

class SubjectsSerializer(serializers.ModelSerializer):
    model = Subject


class GradeSerializer(serializers.ModelSerializer):
    class_teacher = serializers.StringRelatedField()
    class Meta:
        model = Grade
        fields = ['id','name','class_teacher']


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields ='__all__'

# ==================  Library =======================
class BookSerializer(serializers.ModelSerializer):
    grade = serializers.PrimaryKeyRelatedField(queryset=Grade.objects.all())
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    class Meta:
        model = Book
        fields = '__all__'

class IssuedBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssuedBooks
        fields = '__all__'


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabEquipment
        fields = '__all__'