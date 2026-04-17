from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from apps.common.models import BaseModel

class Category(BaseModel):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Yangilik kategoriyasi"
        verbose_name_plural = "Yangilik kategoriyalari"

class News(BaseModel):
    category = models.ForeignKey(Category, related_name='news', on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    summary = models.TextField(max_length=500, null=True, blank=True)
    content = models.TextField()
    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    main_image = models.ImageField(upload_to='news/', null=True, blank=True)
    is_published = models.BooleanField(default=True)

    def _get_slug_source_title(self) -> str:
        default_language = getattr(
            settings,
            'MODELTRANSLATION_DEFAULT_LANGUAGE',
            settings.LANGUAGE_CODE,
        ).split('-', maxsplit=1)[0]
        translated_title = getattr(self, f'title_{default_language}', None)
        return translated_title or self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self._get_slug_source_title()) or 'news'
            candidate = base_slug
            suffix = 2
            while News.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f'{base_slug}-{suffix}'
                suffix += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Yangilik"
        verbose_name_plural = "Yangiliklar"
        ordering = ['-published_at', '-created_at']


class NewsImage(BaseModel):
    news = models.ForeignKey(News, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news/gallery/')
    caption = models.CharField(max_length=255, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.news.title} - image {self.order}"

    class Meta:
        verbose_name = "Yangilik rasmi"
        verbose_name_plural = "Yangilik rasmlari"
        ordering = ['order', 'id']


class NewsVideo(BaseModel):
    news = models.ForeignKey(News, related_name='videos', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)
    video = models.FileField(upload_to='news/videos/', null=True, blank=True)
    video_url = models.URLField(max_length=1000, null=True, blank=True)
    preview_image = models.ImageField(upload_to='news/video_previews/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if not self.video and not self.video_url:
            raise ValidationError({
                'video': "Video fayl yoki video URL kiritilishi shart.",
                'video_url': "Video fayl yoki video URL kiritilishi shart.",
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.title:
            return self.title
        return f"{self.news.title} - video {self.order}"

    class Meta:
        verbose_name = "Yangilik videosi"
        verbose_name_plural = "Yangilik videolari"
        ordering = ['order', 'id']
