from django.conf import settings
from django.db import models
from django.utils import translation
from django.utils.text import slugify


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class History(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='history/', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Universitet tarixi'
        verbose_name_plural = 'Universitet tarixi'


class StaticPage(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()

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
        max_length = self._meta.get_field(field_name).max_length or 50
        base_slug = slugify(value) or 'page'

        def normalize_slug(suffix: int | None = None) -> str:
            if suffix is None:
                return base_slug[:max_length]

            suffix_text = f'-{suffix}'
            allowed = max_length - len(suffix_text)
            if allowed < 1:
                return suffix_text[-max_length:]
            return f"{base_slug[:allowed]}{suffix_text}"

        candidate = normalize_slug()
        suffix = 2

        while StaticPage.objects.filter(**{field_name: candidate}).exclude(pk=self.pk).exists():
            candidate = normalize_slug(suffix)
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
        verbose_name = 'Statik sahifa'
        verbose_name_plural = 'Statik sahifalar'


class SliderCategory(BaseModel):
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Slider kategoriyasi'
        verbose_name_plural = 'Slider kategoriyalari'
        ordering = ['order', 'id']


class SliderItem(BaseModel):
    category = models.ForeignKey(
        SliderCategory,
        on_delete=models.SET_NULL,
        related_name='slider_items',
        blank=True,
        null=True,
        db_column='category_ref_id',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='sliders/', blank=True, null=True)
    video = models.FileField(upload_to='sliders/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Slider elementi'
        verbose_name_plural = 'Slider elementlari'
        ordering = ['order']
