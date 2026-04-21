from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from apps.common.language import (
    LanguageAwareReadOnlyModelViewSet,
    build_language_query_parameter,
)
from .models import Category, News, NewsImage, NewsVideo
from .serializers import (
    CategorySerializer,
    NewsDetailSerializer,
    NewsListSerializer,
)

LANGUAGE_QUERY_PARAMETER = build_language_query_parameter()
NEWS_CATEGORY_QUERY_PARAMETER = OpenApiParameter(
    name='category',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    required=False,
    description='Yangiliklarni kategoriya ID bo‘yicha filterlaydi.',
)

@extend_schema_view(
    list=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
    retrieve=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
)
@extend_schema(tags=['News'])
class CategoryViewSet(LanguageAwareReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer

@extend_schema_view(
    list=extend_schema(
        parameters=[
            LANGUAGE_QUERY_PARAMETER,
            NEWS_CATEGORY_QUERY_PARAMETER,
        ],
    ),
    retrieve=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
)
@extend_schema(tags=['News'])
class NewsViewSet(LanguageAwareReadOnlyModelViewSet):
    queryset = News.objects.filter(is_published=True).select_related('category')
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action == 'list':
            category_id = self.request.query_params.get('category')
            if category_id:
                normalized_category_id = category_id.strip()
                if not normalized_category_id.isdigit():
                    return queryset.none()
                queryset = queryset.filter(
                    category_id=int(normalized_category_id),
                )

        if self.action in {'retrieve', 'by_id'}:
            return queryset.prefetch_related(
                Prefetch(
                    'images',
                    queryset=NewsImage.objects.filter(is_active=True).order_by('order', 'id'),
                    to_attr='active_images',
                ),
                Prefetch(
                    'videos',
                    queryset=NewsVideo.objects.filter(is_active=True).order_by('order', 'id'),
                    to_attr='active_videos',
                ),
            )
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NewsDetailSerializer
        return NewsListSerializer

    @extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER])
    @action(detail=False, methods=['get'], url_path=r'by-id/(?P<pk>\d+)')
    def by_id(self, request, pk=None):
        obj = get_object_or_404(self.filter_queryset(self.get_queryset()), pk=pk)
        serializer = NewsDetailSerializer(obj, context=self.get_serializer_context())
        return Response(serializer.data)
