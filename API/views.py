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
from Students.models import Student
from Subjects.models import Subject, Grade
from Exams.models import Exam, StudentPerformance
# Create your views here.

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

# ========================== STUDENTS ====================================
class StudentViewset(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentListSerializer

    def get_queryset(self):
        queryset = Student.objects.all()

        gradeId = self.request.query_params.get('gradeId')
        grade = get_object_or_404(Grade, id=gradeId)
        if grade:
            queryset = queryset.filter(grade=grade)

        return queryset

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

