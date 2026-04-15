from rest_framework import serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from .models import History, StaticPage, Slider, SliderItem


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = (
            'id',
            'title',
            'content',
            'image',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = (
            'id',
            'title',
            'slug',
            'content',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class SliderItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    url = serializers.URLField(source='link', allow_null=True, required=False)

    @extend_schema_field(OpenApiTypes.URI)
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            image_name = obj.image.name
            if obj.image.storage.exists(image_name):
                image_url = obj.image.url
                if request:
                    return request.build_absolute_uri(image_url)
                return image_url
        return obj.link

    class Meta:
        model = SliderItem
        fields = (
            'id',
            'title',
            'image',
            'url',
            'order',
        )
        read_only_fields = ('id',)


class SliderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    @extend_schema_field(SliderItemSerializer(many=True))
    def get_items(self, obj):
        items = getattr(obj, 'active_items', None)
        if items is None:
            items = obj.items.filter(is_active=True).order_by('order')
        return SliderItemSerializer(
            items,
            many=True,
            context=self.context,
        ).data

    class Meta:
        model = Slider
        fields = (
            'id',
            'title',
            'is_active',
            'order',
            'items',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
