from rest_framework import serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from apps.common.language import LanguageMetadataSerializerMixin
from .models import Category, News, NewsImage, NewsVideo


class CategorySerializer(LanguageMetadataSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'id',
            'title',
            'language',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = (
            'id',
            'image',
            'caption',
            'order',
        )
        read_only_fields = ('id',)


class NewsVideoSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.URI)
    def get_source(self, obj):
        request = self.context.get('request')
        if obj.video:
            video_url = obj.video.url
            if request:
                return request.build_absolute_uri(video_url)
            return video_url
        return obj.video_url

    class Meta:
        model = NewsVideo
        fields = (
            'id',
            'title',
            'video',
            'video_url',
            'source',
            'preview_image',
            'order',
        )
        read_only_fields = ('id',)


class NewsListSerializer(LanguageMetadataSerializerMixin, serializers.ModelSerializer):
    category_title = serializers.CharField(source='category.title', read_only=True)
    short_description = serializers.CharField(source='summary', read_only=True, allow_null=True)

    class Meta:
        model = News
        fields = (
            'id',
            'category',
            'category_title',
            'title',
            'slug',
            'short_description',
            'summary',
            'main_image',
            'published_at',
            'language',
            'is_published',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')


class NewsDetailSerializer(NewsListSerializer):
    content_paragraphs = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_content_paragraphs(self, obj):
        if not obj.content:
            return []

        normalized_content = obj.content.replace('\r\n', '\n')
        blocks = [block.strip() for block in normalized_content.split('\n\n')]
        return [block for block in blocks if block]

    @extend_schema_field(NewsImageSerializer(many=True))
    def get_images(self, obj):
        images = getattr(obj, 'active_images', None)
        if images is None:
            images = obj.images.filter(is_active=True).order_by('order', 'id')
        return NewsImageSerializer(images, many=True, context=self.context).data

    @extend_schema_field(NewsVideoSerializer(many=True))
    def get_videos(self, obj):
        videos = getattr(obj, 'active_videos', None)
        if videos is None:
            videos = obj.videos.filter(is_active=True).order_by('order', 'id')
        return NewsVideoSerializer(videos, many=True, context=self.context).data

    class Meta(NewsListSerializer.Meta):
        fields = NewsListSerializer.Meta.fields + (
            'content',
            'content_paragraphs',
            'images',
            'videos',
        )
