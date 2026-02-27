from django.urls import path
from . import views
urlpatterns = [
    path('', views.TimeTable.as_view(), name="timetable"),
    path("api/timetable/<int:grade_id>/", views.GradeTimetableAPIView.as_view(), name="grade-timetable"),
    path('edit/<int:grade_id>/', views.timetable_matrix_view, name='edit_timetable')
]