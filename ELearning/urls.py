from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name='home_page'),
    path('manage/', views.GradeList.as_view(), name='elearning_home'),
    path('subjects/list/<int:grade_id>/', views.SubjectsList.as_view(), name='subjects_list_page'),
    path('subjects/strands/list/<int:subject_id>/', views.StrandsList.as_view(),name='strands_list'),
    #path('manage-portal/content/',views.ManageContentView.as_view(), name='manage_content_simple'),
    #path('api/strands/', views.StrandListView.as_view(), name='api_strands'),
    path('substrands/<int:strand_id>/', views.SubStrandListView.as_view(), name='api_substrands'),
    #path('api/notes/', views.NoteListView.as_view(), name='api_notes'),
    path('api/subjects/<int:subject_id>/add-strand/', views.AddStrandAPI.as_view(), name='api_add_strand'),
    path('api/add-substrand/', views.AddSubStrandView.as_view(), name='add_substrand'),
    path('add-note/<int:substrand_id>/', views.AddNoteView.as_view(), name='add_notes'),
    path('api/note/', views.NoteDetailView.as_view(), name='save_resources'),
    path('api/save-notes/', views.save_notes, name='save_notes'),
    path('api/save-image/', views.save_image, name='save_image'),
    path('api/save-video/', views.save_video, name='save_video'),
    #========================Learners View URLConfig ======================================================
    path('learners/grades/list/',views.LearnersGradeList.as_view(),name='learners_grades_list'),
    path('<int:grade_id>/subject/list/', views.GradeSubjectList.as_view(), name='grade_subject_list'),
    path('subject/<int:subject_id>/strand/list/', views.SubjectStrandsList.as_view(), name='subject_strands'),
    path('strands/<int:strand_id>/substrands/list/', views.SubStrandsList.as_view(),name='substrands_list')
]
