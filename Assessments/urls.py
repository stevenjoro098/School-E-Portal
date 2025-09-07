from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.Home, name='assessment_home'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('create/assessment/', views.AssessmentCreate.as_view(), name='create_assessment'),
    path('publish/assessment/<int:pk>/', views.AssessmentPublish.as_view(), name='publish_assessment'),
    path('edit/<int:assessment_id>/question/<int:pk>/', views.AssessmentEditView.as_view(), name='edit_assessment'),
    path('edit/assessment/<int:pk>/', views.AssessmentEditView.as_view(), name='assessment_edit'),
    path('delete/<int:pk>/', views.AssessmentDelete.as_view(), name='delete_assessment'),
    path('create/questions/form/<int:assessment_id>/', views.QuestionCreateView.as_view(), name='create_questions'),
    path('questions/<int:assessment_id>/edit/<int:pk>/', views.QuestionUpdateView.as_view(), name='update_question'),
    path('questions/list/<int:assessment_id>/', views.QuestionsListView.as_view(), name='questions_list'),
    path('take/assessment/<int:assessment_id>/', views.take_assessment, name='take_assessment'),
    path('check/assessment/<int:assessment_id>/', views.check_if_taken, name='check_attempt'),
    path('assessment/<int:assessment_id>/submit/', views.SubmitAssessmentView.as_view(), name='submit_assessment'),
    path('assessment/analysis/<int:assessment_id>', views.AssessmentAnalysis.as_view(), name='assessment_analysis'),
    path('assessment/analysis/pdf/<int:assessment_id>/', views.generate_assessment_summary_pdf, name='assessment_analysis_pdf'),
    path('result/<int:pk>/', views.AssessmentResultView.as_view(), name='assessment_result'),
    path('results/<int:result_id>/pdf/', views.download_result_pdf, name='download_result_pdf'),
    path('questions/list/pdf/<int:assessment_id>/', views.questions_list_pdf, name='questions_list_pdf')
]
