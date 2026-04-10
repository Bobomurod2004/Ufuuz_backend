from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import CategoryViewSet, NewsViewSet

router = SimpleRouter()
router.register('categories', CategoryViewSet)
router.register('news', NewsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
