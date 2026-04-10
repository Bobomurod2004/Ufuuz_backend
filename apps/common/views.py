from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from .models import History, StaticPage
from .serializers import HistorySerializer, StaticPageSerializer

@extend_schema(tags=['Common'])
class HistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = History.objects.all()
    serializer_class = HistorySerializer

@extend_schema(tags=['Common'])
class StaticPageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    lookup_field = 'slug'
