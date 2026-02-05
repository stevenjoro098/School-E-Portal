from django.urls import path
from . import views
urlpatterns = [
    path('', views.TimeTable.as_view(), name="timetable"),
# urls.py
    path("api/timetable/<int:grade_id>/", views.GradeTimetableAPIView.as_view(), name="grade-timetable"),

    path('edit', views.timetable_matrix_view, name='edit')
]