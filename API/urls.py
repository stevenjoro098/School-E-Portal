from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'students', views.StudentViewset)
#router.register(r'subjects', SubjectViewSet)
router.register(r'exams', views.ExamViewset)
router.register(r'grades', views.GradeViewSet)
router.register(r'books', views.BooksViewsets)
router.register(r'issued-books', views.IssueBooksViewset)

urlpatterns = router.urls