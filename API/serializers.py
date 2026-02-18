from rest_framework import serializers
from Students.models import Student, Teachers
from Subjects.models import Subject, Grade
from Exams.models import Exam


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
