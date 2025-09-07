from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name='home_page'),
    path('manage/', views.GradeList.as_view(), name='elearning_home'),
    path('subjects/list/<int:grade_id>/', views.SubjectsList.as_view(), name='subjects_list_page'),
    path('subjects/add/form/page/<int:grade_id>/', views.AddSubjectView.as_view(), name='add_subject'),
    path('subjects/strands/list/<int:subject_id>/', views.StrandsList.as_view(),name='strands_list'),
    path('subject/delete/<int:grade_id>/<int:pk>/', views.SubjectDelete.as_view(), name='delete_subject'),
    path('substrand/resources/view/<int:substrand_id>/', views.SubstrandResourceView.as_view(), name='resources_view'),

    path('substrands/<int:strand_id>/', views.SubStrandListView.as_view(), name='api_substrands'),

    path('delete/image/<int:pk>/<int:substrand_id>/', views.ImageDeleteView.as_view(), name='delete_image'),
    path('delete/notes/<int:pk>/<int:substrand_id>/', views.NoteDeleteView.as_view(), name='delete_notes'),
    path('delete/strand/<int:pk>/<int:subject_id>/', views.StrandDelete.as_view(), name='strand_delete'),

    path('api/subjects/<int:subject_id>/add-strand/', views.AddStrandAPI.as_view(), name='api_add_strand'),
    path('api/add-substrand/', views.AddSubStrandView.as_view(), name='add_substrand'),
    path('add-note/<int:substrand_id>/', views.AddNoteView.as_view(), name='add_notes'),
    path('note/edit/<int:pk>/<int:substrand_id>/', views.NoteEditView.as_view(),name='edit_notes'),
    path('api/save-notes/', views.save_notes, name='save_notes'),
    path('api/save-image/', views.save_image, name='save_image'),
    path('api/save-video/', views.save_video, name='save_video'),
    #========================Learners View URLConfig ======================================================
    path('learners/grades/list/',views.LearnersGradeList.as_view(),name='learners_grades_list'),
    path('<int:grade_id>/subject/list/', views.GradeSubjectList.as_view(), name='grade_subject_list'),
    path('subject/<int:subject_id>/strand/list/', views.SubjectStrandsList.as_view(), name='subject_strands'),
    path('strands/<int:strand_id>/substrands/list/', views.SubStrandsList.as_view(),name='substrands_list')
]
