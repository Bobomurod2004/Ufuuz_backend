from django.conf import settings
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.language import (
    LanguageAwareReadOnlyModelViewSet,
    build_language_query_parameter,
    get_default_language,
)

from .models import History, SliderCategory, SliderItem, StaticPage
from .serializers import (
    HistorySerializer,
    LanguagesResponseSerializer,
    SliderCategorySerializer,
    SliderItemSerializer,
    StaticPageSerializer,
)


LANGUAGE_QUERY_PARAMETER = build_language_query_parameter()


@extend_schema_view(
    list=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
    retrieve=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
)
@extend_schema(tags=['Common'])
class HistoryViewSet(LanguageAwareReadOnlyModelViewSet):
    queryset = History.objects.all().order_by('id')
    serializer_class = HistorySerializer


@extend_schema_view(
    list=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
    retrieve=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
)
@extend_schema(tags=['Common'])
class StaticPageViewSet(LanguageAwareReadOnlyModelViewSet):
    queryset = StaticPage.objects.all().order_by('id')
    serializer_class = StaticPageSerializer
    lookup_field = 'slug'

    @extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER])
    @action(detail=False, methods=['get'], url_path=r'by-id/(?P<pk>\d+)')
    def by_id(self, request, pk=None):
        obj = get_object_or_404(
            self.filter_queryset(self.get_queryset()),
            pk=pk,
        )
        serializer = self.get_serializer(obj)
        return Response(serializer.data)


class SliderCategoryViewSet(LanguageAwareReadOnlyModelViewSet):
    queryset = SliderCategory.objects.filter(is_active=True).order_by('order')
    serializer_class = SliderCategorySerializer


@extend_schema_view(
    list=extend_schema(
        summary="Slider items ro'yxatini olish",
        description='Barcha faol slider itemlarini kategoriya bo\'ylab tartiblangan holda qaytaradi',
        parameters=[LANGUAGE_QUERY_PARAMETER],
        tags=['Slider'],
    ),
    retrieve=extend_schema(
        summary='Slider item detallari',
        description='Muayyan slider item\'ning to\'lik ma\'lumotlarini qaytaradi',
        parameters=[LANGUAGE_QUERY_PARAMETER],
        tags=['Slider'],
    ),
)
class SliderItemViewSet(LanguageAwareReadOnlyModelViewSet):
    """
    Slider Item ViewSet
    
    Slider items - saytning asosiy slider elementlari
    Har bir item: title, description, image, video, category
    
    Endpoints:
    - GET /api/v1/common/slider-items/ - barcha faol itemlar
    - GET /api/v1/common/slider-items/{id}/ - bir item detallari
    
    Query parameters:
    - lang=uz|en|fr - til belgilash (default: uz)
    """
    queryset = SliderItem.objects.filter(
        is_active=True,
    ).select_related('category').order_by('order')
    serializer_class = SliderItemSerializer


@extend_schema(
    tags=['Common'],
    responses=LanguagesResponseSerializer,
)
class SupportedLanguageAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        payload = {
            'default_language': get_default_language(),
            'languages': [
                {'code': code, 'name': str(name)}
                for code, name in settings.LANGUAGES
            ],
        }
        return Response(payload)
