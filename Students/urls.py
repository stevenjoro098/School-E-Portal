from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.StudentDetailView.as_view(), name='student_details_view'),
    path('create/', views.StudentCreateView.as_view(), name='student_register'),
    path('find/', views.SearchStudentPage.as_view(), name='find_student'),
    path('update/<int:pk>/', views.UpdateStudent.as_view(),name='update_student'),
    path('students/by-grade/<int:grade_id>/', views.StudentsByGradeView.as_view(), name='students_by_grade'),
]