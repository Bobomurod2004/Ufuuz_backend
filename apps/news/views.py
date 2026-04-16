from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Category, News
from .serializers import CategorySerializer, NewsSerializer

@extend_schema_view(
    retrieve=extend_schema(exclude=True),
)
@extend_schema(tags=['News'])
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer

@extend_schema(tags=['News'])
class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.filter(is_published=True).select_related('category')
    serializer_class = NewsSerializer
    lookup_field = 'slug'
