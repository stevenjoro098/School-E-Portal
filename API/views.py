from django.shortcuts import render
from rest_framework import generics, viewsets

from Library.models import Book, IssuedBooks
from .serializers import IssuedBookSerializer, StudentListSerializer, SubjectsSerializer, ExamSerializer, BookSerializer
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

# ==================== Library ==============================================
class BooksViewsets(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class IssueBooksViewset(viewsets.ModelViewSet):
    queryset = IssuedBooks.objects.all()
    serializer_class = IssuedBookSerializer