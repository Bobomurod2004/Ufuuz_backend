from django.db import models
from apps.common.models import BaseModel

class Faculty(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='faculties/', null=True, blank=True)
    icon = models.FileField(upload_to='faculties/icons/', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Fakultet"
        verbose_name_plural = "Fakultetlar"

class Department(BaseModel):
    faculty = models.ForeignKey(Faculty, related_name='departments', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    head_name = models.CharField(max_length=255, null=True, blank=True)
    contact_info = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Kafedra"
        verbose_name_plural = "Kafedralar"
