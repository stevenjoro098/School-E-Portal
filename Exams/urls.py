from django.urls import path
from . import views

urlpatterns = [
    path('', views.GradesList.as_view(), name='exams'),
    path('grade/<int:pk>/exam/list', views.ExamsList.as_view(), name='exam_list'),
    path('performance/student/<int:id>/<int:pk>/', views.StudentPerformanceDetailView.as_view(), name='student_details_performance'),
    path('create/exam/', views.CreateExam.as_view(), name='create_exam'),
    path("exam/<int:pk>/performance/", views.EnterExamPerformanceView.as_view(), name="enter_exam_performance"),
    path("exam/<int:pk>/performances/", views.ExamPerformanceListView.as_view(), name="exam_performance_list"),
    path("<int:pk>/performance/", views.ExamPerformanceListView.as_view(), name="exam_performance_list"),
    path("<int:pk>/performance/excel/", views.ExportExamExcelView.as_view(), name="export_exam_excel"),
    path("<int:pk>/performance/pdf/", views.ExportExamPDFView.as_view(), name="export_exam_pdf"),
]
