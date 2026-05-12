from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import StudentApplicationViewSet


router = SimpleRouter()
router.register('applications', StudentApplicationViewSet, basename='admissions-applications')

urlpatterns = [
    path('', include(router.urls)),
]
