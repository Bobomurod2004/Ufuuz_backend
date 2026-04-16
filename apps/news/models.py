from django.db import models
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
    main_image = models.ImageField(upload_to='news/', null=True, blank=True)
    is_published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'news'
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
        ordering = ['-created_at']
