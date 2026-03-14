from django.urls import path
from . import views

urlpatterns = [
    path('', views.GradesList.as_view(), name='exams'),
    path("exam/<int:exam_id>/subject/<int:subject_id>/review/",views.SubjectReviewView.as_view(),name="subject_review"),
    path('grade/<int:pk>/exam/list', views.ExamsList.as_view(), name='exam_list'),
    path('student/<int:student_id>/exam/<int:exam_id>/term-summary/', views.StudentTermExamSummaryView.as_view(),name='student_term_exam_summary'),
    path('student/<int:pk>/exam/<int:id>/pdf/view/', views.StudentSingleExamPDF.as_view(), name='student_exam_pdf_view'),
    path('grade/<int:grade_id>/term/<str:term>/print-report-cards/',views.PrintTermReportCardsView.as_view(), name='print_term_report_cards'),
    path('teacher/exam/performance/<int:teacher_id>/<int:exam_id>/', views.TeacherSubjectExamPerformanceView.as_view(), name='teacher_performance'),
    path('term/exam/analysis/<int:grade_id>/<str:term>/', views.TermExamAnalysis.as_view(), name='term_analysis'),
    path('performance/student/<int:id>/<int:pk>/', views.StudentPerformanceDetailView.as_view(), name='student_details_performance'),
    path('pdf/student/performance/<int:exam_id>/<int:student_id>/', views.ExportStudentPDFView.as_view(), name='student_performance_pdf'),
    path('pdf/students/performance/<int:exam_id>/', views.ExportClassPDFView.as_view(), name='generate_class_report'),
    path('create/exam/', views.CreateExam.as_view(), name='create_exam'),
    path("exam/<int:pk>/performance/", views.EnterExamPerformanceView.as_view(), name="enter_exam_performance"),
    path("exam/<int:pk>/performances/", views.ExamPerformanceListView.as_view(), name="exam_performance_list"),
    path('exam/pdf/report/card/<int:exam_id>', views.GenerateClassReportCardsView.as_view(), name='exam_report_cards'),
    path("<int:pk>/performance/", views.ExamPerformanceListView.as_view(), name="exam_performance_list"),
    path("<int:pk>/performance/excel/", views.ExportExamExcelView.as_view(), name="export_exam_excel"),
    path("<int:pk>/performance/pdf/", views.ExportExamPDFView.as_view(), name="export_exam_pdf"),
path(
    'exam/select-report-exams/<int:grade_id>/<term>/',
    views.SelectReportExams.as_view(),
    name='select_report_exams'
),

path(
    'exam/<int:grade_id>/generate-selected-reports/<str:term>/',
    views.PrintTermReportCardsView.as_view(),
    name='generate_pdf_selected_exam'
),


]


