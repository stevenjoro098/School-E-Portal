from itertools import count

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from Laboratory.models import LabEquipment
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from Library.models import Book, IssuedBooks
from .serializers import GradeSerializer, IssuedBookSerializer, StudentListSerializer, SubjectsSerializer, \
    ExamSerializer, BookSerializer, LabSerializer
from Students.models import Student, Teachers
from Subjects.models import Subject, Grade
from Exams.models import Exam, StudentPerformance
# Create your views here.

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

# ========================== STUDENTS ====================================
class StudentViewset(viewsets.ModelViewSet):
    queryset = Student.objects.all()  # ✅ REQUIRED for DRF router
    serializer_class = StudentListSerializer

    def get_queryset(self):
        queryset = Student.objects.all()

        grade_id = self.request.query_params.get('gradeId')

        # ✅ ONLY filter if gradeId exists
        if grade_id:
            queryset = queryset.filter(grade_id=grade_id)

        return queryset


    @action(detail=False, methods=['get'])
    def count(self, request):
        count = Student.objects.filter(active=True).count()
        teachers = Teachers.objects.all().count()
        return Response({'student_count':str(count),
                         'teachers_count': str(teachers)})

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '').strip()

        # ❌ reject empty or too short queries
        if len(query) < 2:
            return Response([])

        students = Student.objects.filter(
            Q(first_name__icontains=query) |
            Q(second_name__icontains=query)|
            Q(third_name__icontains=query)
        )[:20]  # 🔥 limit results (important)
        print(students)
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)
# ================= Subject ==================================================
class SubjectListCreate(generics.ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectsSerializer

class SubjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectsSerializer

# ========================= EXAM =======================================

class ExamViewset(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

    def get_queryset(self):
        queryset = Exam.objects.all()
        gradeId = self.request.query_params.get('gradeId')

        if gradeId:
            grade = get_object_or_404(Grade, id=gradeId)
            queryset = queryset.filter(grade=grade)

        return queryset

    # ✅ NEW: analysis endpoint
    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        exam = self.get_object()

        # 📊 Subject averages
        subject_averages = (
            StudentPerformance.objects
            .filter(exam=exam)
            .values('subject__name')
            .annotate(avg_score=Avg('performance'))
            .order_by('-avg_score')
        )

        # 👨‍🎓 Student averages
        student_averages = (
            StudentPerformance.objects
            .filter(exam=exam)
            .values('student_id', 'student_name')
            .annotate(
                avg_score=Avg('performance'),
                total_subjects=Count('subject')
            )
            .order_by('-avg_score')
        )

        return Response({
            "exam": exam.exam_name,
            "subject_averages": subject_averages,
            "student_averages": student_averages
        })

# ==================== Library ==============================================
class BooksViewsets(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @action(detail=False, methods=['get'])
    def count(self, request):
        books_count = Book.objects.all().count()
        return Response({'books_count': str(books_count)})

class SearchBook(APIView):
    def post(self, *args, **kwargs):
        query = self.request.GET.get('q')
        searched_book = Book.objects.filter(
                Q(name__icontains=query)
            )
        return Response({'results': searched_book })


class IssueBooksViewset(viewsets.ModelViewSet):
    queryset = IssuedBooks.objects.all()
    serializer_class = IssuedBookSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {"success": "Book issued successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            # Returns JSON with the validation errors
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Returns JSON for any unexpected server error
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ======================Laboratory ======================================================
class LabViewSet(viewsets.ModelViewSet):
    queryset = LabEquipment.objects.all()
    serializer_class = LabSerializer

