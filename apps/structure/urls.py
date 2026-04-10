from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import FacultyViewSet, DepartmentViewSet

router = SimpleRouter()
router.register('faculties', FacultyViewSet)
router.register('departments', DepartmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
