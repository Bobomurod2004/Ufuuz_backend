from django.db import models
from django.core.exceptions import ValidationError

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
        verbose_name = "Universitet tarixi"
        verbose_name_plural = "Universitet tarixi"

class StaticPage(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Statik sahifa"
        verbose_name_plural = "Statik sahifalar"

class Slider(BaseModel):
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Slider"
        verbose_name_plural = "Sliderlar"
        ordering = ['order']

class SliderItem(BaseModel):
    slider = models.ForeignKey(
        Slider,
        on_delete=models.CASCADE,
        related_name='items',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to='sliders/',
        blank=True,
        null=True,
        help_text=(
            "Rasm fayl yuklang. "
            "Agar fayl bo'lmasa, pastdagi Image URL ni kiriting."
        ),
    )
    link = models.URLField(
        "Image URL",
        blank=True,
        null=True,
        help_text="Tashqi rasm URL manzili (https://...).",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if not self.image and not self.link:
            raise ValidationError({
                'image': "Rasm yoki Image URL kiritilishi shart.",
                'link': "Rasm yoki Image URL kiritilishi shart.",
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.slider_id is None:
            default_slider, _ = Slider.objects.get_or_create(
                title='Asosiy Slider',
                defaults={'is_active': True, 'order': 0},
            )
            self.slider = default_slider
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.slider.title} - {self.title}"

    class Meta:
        verbose_name = "Slider elementi"
        verbose_name_plural = "Slider elementlari"
        ordering = ['order']
