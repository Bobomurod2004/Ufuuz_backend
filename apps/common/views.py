from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.models import Prefetch
from .models import History, StaticPage, Slider, SliderItem
from .serializers import HistorySerializer, StaticPageSerializer, SliderSerializer, SliderItemSerializer

@extend_schema_view(
    retrieve=extend_schema(exclude=True),
)
@extend_schema(tags=['Common'])
class HistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = History.objects.all().order_by('id')
    serializer_class = HistorySerializer

@extend_schema(tags=['Common'])
class StaticPageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StaticPage.objects.all().order_by('id')
    serializer_class = StaticPageSerializer
    lookup_field = 'slug'

@extend_schema_view(
    retrieve=extend_schema(exclude=True),
)
@extend_schema(tags=['Common'])
class SliderViewSet(viewsets.ReadOnlyModelViewSet):
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

@extend_schema(exclude=True)
class SliderItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SliderItem.objects.filter(is_active=True, slider__is_active=True).order_by('order')
    serializer_class = SliderItemSerializer
