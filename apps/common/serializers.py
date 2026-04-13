from rest_framework import serializers
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
    class Meta:
        model = SliderItem
        fields = (
            'id',
            'title',
            'description',
            'image',
            'link',
            'order',
            'is_active',
        )
        read_only_fields = ('id',)


class SliderSerializer(serializers.ModelSerializer):
    items = SliderItemSerializer(many=True, read_only=True)

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
