from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.models import Prefetch
from apps.common.language import (
    LanguageAwareReadOnlyModelViewSet,
    build_language_query_parameter,
    get_default_language,
)
from .models import History, StaticPage, Slider, SliderItem
from .serializers import (
    HistorySerializer,
    LanguagesResponseSerializer,
    SliderItemSerializer,
    SliderSerializer,
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
        obj = get_object_or_404(self.filter_queryset(self.get_queryset()), pk=pk)
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

@extend_schema_view(
    list=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
    retrieve=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
)
@extend_schema(tags=['Common'])
class SliderViewSet(LanguageAwareReadOnlyModelViewSet):
    queryset = Slider.objects.filter(
        is_active=True
    ).order_by('order', 'id').prefetch_related(
        Prefetch(
            'items',
            queryset=SliderItem.objects.filter(is_active=True).order_by('order'),
            to_attr='active_items',
        )
    )
    serializer_class = SliderSerializer

@extend_schema_view(
    list=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
    retrieve=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
)
@extend_schema(tags=['Common'])
class SliderItemViewSet(LanguageAwareReadOnlyModelViewSet):
    queryset = SliderItem.objects.filter(is_active=True, slider__is_active=True).order_by('order')
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
