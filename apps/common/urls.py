from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    HistoryViewSet,
    SliderItemViewSet,
    SliderViewSet,
    StaticPageViewSet,
    SupportedLanguageAPIView,
)

router = SimpleRouter()
router.register('history', HistoryViewSet)
router.register('pages', StaticPageViewSet)
router.register('sliders', SliderViewSet)
router.register('slider-items', SliderItemViewSet)

urlpatterns = [
    path('languages/', SupportedLanguageAPIView.as_view(), name='supported-languages'),
    path('', include(router.urls)),
]
