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
    slider = models.ForeignKey(Slider, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='sliders/')
    link = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.slider.title} - {self.title}"

    class Meta:
        verbose_name = "Slider elementi"
        verbose_name_plural = "Slider elementlari"
        ordering = ['order']
