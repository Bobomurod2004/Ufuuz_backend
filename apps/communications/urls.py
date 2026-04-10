from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ContactViewSet, SocialLinkViewSet

router = SimpleRouter()
router.register('contact', ContactViewSet)
router.register('social-links', SocialLinkViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
