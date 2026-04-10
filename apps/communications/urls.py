from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet, SocialLinkViewSet

router = DefaultRouter()
router.register('contact', ContactViewSet)
router.register('social-links', SocialLinkViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
