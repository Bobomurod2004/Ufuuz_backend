from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HistoryViewSet, StaticPageViewSet

router = DefaultRouter()
router.register('history', HistoryViewSet)
router.register('pages', StaticPageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
