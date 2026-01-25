from django.urls import path
from . import views
urlpatterns = [
    path('edit', views.timetable_matrix_view, name='edit')
]