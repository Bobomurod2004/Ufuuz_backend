from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from django.db.models import Prefetch
from .models import History, StaticPage, Slider, SliderItem
from .serializers import HistorySerializer, StaticPageSerializer, SliderSerializer, SliderItemSerializer

@extend_schema(tags=['Common'])
class HistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = History.objects.all()
    serializer_class = HistorySerializer

@extend_schema(tags=['Common'])
class StaticPageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    lookup_field = 'slug'

@extend_schema(tags=['Common'])
class SliderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Slider.objects.filter(is_active=True).prefetch_related(
        Prefetch(
            'items',
            queryset=SliderItem.objects.filter(is_active=True).order_by('order'),
            to_attr='active_items',
        )
    )
    serializer_class = SliderSerializer

@extend_schema(tags=['Common'])
class SliderItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SliderItem.objects.filter(is_active=True, slider__is_active=True).order_by('order')
    serializer_class = SliderItemSerializer
