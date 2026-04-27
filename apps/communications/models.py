from django.db import models
from apps.common.models import BaseModel

class Contact(BaseModel):
    address = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    working_hours = models.CharField(max_length=255, null=True, blank=True)
    map_url = models.URLField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.address if self.address else f"Contact {self.id}"

    class Meta:
        verbose_name = "Kontakt ma'lumoti"
        verbose_name_plural = "Kontakt ma'lumotlari"

class ContactAddress(BaseModel):
    contact = models.ForeignKey(Contact, related_name='addresses', on_delete=models.CASCADE)
    address = models.CharField(max_length=500)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = "Manzil"
        verbose_name_plural = "Manzillar"

class ContactPhone(BaseModel):
    contact = models.ForeignKey(Contact, related_name='phones', on_delete=models.CASCADE)
    phone = models.CharField(max_length=255)

    def __str__(self):
        return self.phone

    class Meta:
        verbose_name = "Telefon raqami"
        verbose_name_plural = "Telefon raqamlari"

class ContactEmail(BaseModel):
    contact = models.ForeignKey(Contact, related_name='emails', on_delete=models.CASCADE)
    email = models.EmailField()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Email"
        verbose_name_plural = "Emaillar"

class SocialLink(BaseModel):
    platform = models.CharField(max_length=255)
    url = models.URLField()
    icon = models.FileField(upload_to='social_icons/', null=True, blank=True)

    def __str__(self):
        return self.platform

    class Meta:
        verbose_name = "Ijtimoiy tarmoq"
        verbose_name_plural = "Ijtimoiy tarmoqlar"
