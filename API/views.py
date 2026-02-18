from django.shortcuts import render
from rest_framework import generics
from .serializers import StudentListSerializer, SubjectsSerializer, ExamSerializer
from Students.models import Student
from Subjects.models import Subject
from Exams.models import Exam
# Create your views here.

# ========================== STUDENTS ====================================
class StudentListCreateApiView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentListSerializer

class StudentDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentListSerializer

# ================= Subject ==================================================
class SubjectListCreate(generics.ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectsSerializer

class SubjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectsSerializer

# ========================= EXAM =======================================
class ExamListCreate(generics.ListCreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer