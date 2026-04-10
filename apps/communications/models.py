from django.db import models
from apps.common.models import BaseModel

class Contact(BaseModel):
    address = models.CharField(max_length=500)
    phone = models.CharField(max_length=255)
    email = models.EmailField()
    working_hours = models.CharField(max_length=255, null=True, blank=True)
    map_url = models.URLField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = "Kontakt ma'lumoti"
        verbose_name_plural = "Kontakt ma'lumotlari"

class SocialLink(BaseModel):
    platform = models.CharField(max_length=255)
    url = models.URLField()
    icon = models.FileField(upload_to='social_icons/', null=True, blank=True)

    def __str__(self):
        return self.platform

    class Meta:
        verbose_name = "Ijtimoiy tarmoq"
        verbose_name_plural = "Ijtimoiy tarmoqlar"
