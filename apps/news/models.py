from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils import translation
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

    @staticmethod
    def _get_language_codes() -> tuple[str, ...]:
        return tuple(code for code, _ in settings.LANGUAGES)

    @staticmethod
    def _get_default_language_code() -> str:
        default_language = getattr(
            settings,
            'MODELTRANSLATION_DEFAULT_LANGUAGE',
            settings.LANGUAGE_CODE,
        )
        return default_language.split('-', maxsplit=1)[0]

    def _get_slug_source_title(self, language_code: str) -> str:
        default_language = self._get_default_language_code()
        possible_titles = (
            getattr(self, f'title_{language_code}', None),
            getattr(self, f'title_{default_language}', None),
            self.__dict__.get('title'),
        )

        for title in possible_titles:
            if title:
                return title
        return ''

    def _generate_unique_slug(self, value: str, field_name: str) -> str:
        base_slug = slugify(value) or 'news'
        candidate = base_slug
        suffix = 2

        while News.objects.filter(**{field_name: candidate}).exclude(pk=self.pk).exists():
            candidate = f'{base_slug}-{suffix}'
            suffix += 1

        return candidate

    def _ensure_translated_slugs(self) -> None:
        default_language = self._get_default_language_code()
        default_slug_field = f'slug_{default_language}'
        base_slug = self.__dict__.get('slug') or getattr(self, default_slug_field, None)

        if not getattr(self, default_slug_field, None):
            if base_slug:
                setattr(self, default_slug_field, base_slug)
            else:
                generated_default_slug = self._generate_unique_slug(
                    self._get_slug_source_title(default_language),
                    default_slug_field,
                )
                setattr(self, default_slug_field, generated_default_slug)
                base_slug = generated_default_slug

        with translation.override(default_language):
            self.slug = getattr(self, default_slug_field)

        for language_code in self._get_language_codes():
            slug_field = f'slug_{language_code}'
            if getattr(self, slug_field, None):
                continue

            generated_slug = self._generate_unique_slug(
                self._get_slug_source_title(language_code),
                slug_field,
            )
            setattr(self, slug_field, generated_slug)

    def save(self, *args, **kwargs):
        self._ensure_translated_slugs()
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
