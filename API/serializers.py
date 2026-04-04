from rest_framework import serializers
from Students.models import Student, Teachers
from Subjects.models import Subject, Grade
from Exams.models import Exam
from Library.models import Book, IssuedBooks

# ================ Student List =========================
class StudentListSerializer(serializers.ModelSerializer):
    model = Student

class TeacherSerializer(serializers.ModelSerializer):
    model = Teachers

class SubjectsSerializer(serializers.ModelSerializer):
    model = Subject


class GradeSerializer(serializers.ModelSerializer):
    model = Grade


class ExamSerializer(serializers.ModelSerializer):
    model = Exam

# ==================  Library =======================
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class IssuedBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssuedBooks
        fields = '__all__'