from django.db import models


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
    slug = models.SlugField(unique=True)
    content = models.TextField()

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
