from rest_framework import serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from .models import (
    History,
    SliderCategory,
    SliderItem,
    StaticPage,
)


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


class SliderCategorySerializer(serializers.ModelSerializer):
    """Slider kategoriyasi serializer - categroriyani ifodalaydi"""
    id = serializers.IntegerField(read_only=True, help_text='Kategoriya ID')
    name = serializers.CharField(
        max_length=120,
        help_text='Kategoriya nomi (3 tilda avtomatik tarjima qilinadi)'
    )

    class Meta:
        model = SliderCategory
        fields = ('id', 'name')
        read_only_fields = ('id',)


class SliderItemSerializer(serializers.ModelSerializer):
    """Slider elementi serializer - rasm/video va tavsifi"""
    category = SliderCategorySerializer(
        read_only=True,
        help_text='Slider elementi tegirgan kategoriya'
    )
    image = serializers.SerializerMethodField(
        help_text='Slider uchun rasm (absolute URL)'
    )
    video = serializers.SerializerMethodField(
        help_text='Slider uchun video fayl (absolute URL)'
    )
    title = serializers.CharField(
        max_length=255,
        help_text='Slider sarlavhasi (3 tilda avtomatik tarjima qilinadi)'
    )
    description = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        help_text='Slider tavsifi (3 tilda avtomatik tarjima qilinadi)'
    )
    order = serializers.IntegerField(
        help_text='Tartib raqami (kichikdan kattaga)'
    )

    @extend_schema_field(OpenApiTypes.URI)
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            image_url = obj.image.url
            if request:
                return request.build_absolute_uri(image_url)
            return image_url
        return None

    @extend_schema_field(OpenApiTypes.URI)
    def get_video(self, obj):
        request = self.context.get('request')
        if obj.video:
            video_url = obj.video.url
            if request:
                return request.build_absolute_uri(video_url)
            return video_url
        return None

    class Meta:
        model = SliderItem
        fields = (
            'id',
            'category',
            'title',
            'description',
            'image',
            'video',
            'order',
        )
        read_only_fields = ('id',)


class LanguageOptionSerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()


class LanguagesResponseSerializer(serializers.Serializer):
    default_language = serializers.CharField()
    languages = LanguageOptionSerializer(many=True)
