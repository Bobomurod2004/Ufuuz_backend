from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import HistoryViewSet, StaticPageViewSet

router = SimpleRouter()
router.register('history', HistoryViewSet)
router.register('pages', StaticPageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
