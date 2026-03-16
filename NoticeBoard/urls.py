from django.urls import path

from . import views
urlpatterns = [
    path('', views.NoticeBoardList.as_view(), name='notice_board'),
    path('create/', views.CreateNotice.as_view(), name='create_notice')
]