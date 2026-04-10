from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from .models import Category, News
from .serializers import CategorySerializer, NewsSerializer

@extend_schema(tags=['News'])
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

@extend_schema(tags=['News'])
class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.filter(is_published=True)
    serializer_class = NewsSerializer
    lookup_field = 'slug'
