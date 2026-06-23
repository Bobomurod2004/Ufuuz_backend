from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from apps.common.models import BaseModel


passport_series_validator = RegexValidator(
    regex=r'^[A-Za-z]{2}$',
    message="Passport seriyasi aynan 2 ta harfdan iborat bo'lishi kerak.",
)
passport_number_validator = RegexValidator(
    regex=r'^\d{7}$',
    message="Passport raqami aynan 7 xonali raqam bo'lishi kerak.",
)
phone_number_validator = RegexValidator(
    regex=r'^\+?\d{9,15}$',
    message=(
        "Telefon raqami + belgisi bilan yoki belgisiz "
        "9 dan 15 tagacha raqamdan iborat bo'lishi kerak."
    ),
)


class StudentApplication(BaseModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Kutilmoqda'
        ACCEPTED = 'accepted', 'Qabul qilindi'
        REJECTED = 'rejected', 'Rad etildi'

    first_name = models.CharField(max_length=100, verbose_name='Ism')
    last_name = models.CharField(max_length=100, verbose_name='Familiya')
    middle_name = models.CharField(max_length=100, verbose_name='Otasining ismi')
    passport_series = models.CharField(
        max_length=2,
        validators=[passport_series_validator],
        verbose_name='Pasport seriyasi',
    )
    passport_number = models.CharField(
        max_length=7,
        validators=[passport_number_validator],
        verbose_name='Pasport raqami',
    )
    phone_number = models.CharField(
        max_length=16,
        validators=[phone_number_validator],
        verbose_name='Telefon raqami',
    )
    email = models.EmailField(blank=True, default='', verbose_name='Email manzil')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name='Holat',
    )
    review_note = models.TextField(
        blank=True,
        verbose_name='Ko\'rib chiqish izohi',
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Ko\'rib chiqilgan vaqt',
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='reviewed_student_applications',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Ko\'rib chiqqan xodim',
    )

    class Meta:
        verbose_name = 'Talaba arizasi'
        verbose_name_plural = 'Talaba arizalari'
        ordering = ['-created_at', '-id']

    def clean(self):
        super().clean()
        if self.passport_series:
            self.passport_series = self.passport_series.upper()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.last_name} {self.first_name} ({self.passport_series}{self.passport_number})"
        )


class ApplicationDiploma(BaseModel):
    application = models.ForeignKey(
        StudentApplication,
        related_name='diplomas',
        on_delete=models.CASCADE,
    )
    file = models.FileField(upload_to='admissions/diplomas/')

    class Meta:
        verbose_name = 'Diplom hujjati'
        verbose_name_plural = 'Diplom hujjatlari'
        ordering = ['id']

    def __str__(self):
        return f"Diplom #{self.id} - ariza #{self.application_id}"


class ApplicationCertificate(BaseModel):
    application = models.ForeignKey(
        StudentApplication,
        related_name='certificates',
        on_delete=models.CASCADE,
    )
    file = models.FileField(upload_to='admissions/certificates/')

    class Meta:
        verbose_name = 'Sertifikat'
        verbose_name_plural = 'Sertifikatlar'
        ordering = ['id']

    def __str__(self):
        return f"Sertifikat #{self.id} - ariza #{self.application_id}"


class ApplicationPdf(BaseModel):
    application = models.ForeignKey(
        StudentApplication,
        related_name='application_pdfs',
        on_delete=models.CASCADE,
    )
    file = models.FileField(upload_to='admissions/application_forms/')

    class Meta:
        verbose_name = 'Ariza PDF hujjati'
        verbose_name_plural = 'Ariza PDF hujjatlari'
        ordering = ['id']

    def __str__(self):
        return f"Ariza PDF #{self.id} - ariza #{self.application_id}"


class ApplicationDiplomaSupplement(BaseModel):
    application = models.ForeignKey(
        StudentApplication,
        related_name='diploma_supplements',
        on_delete=models.CASCADE,
    )
    file = models.FileField(upload_to='admissions/diploma_supplements/')

    class Meta:
        verbose_name = 'Diplom ilovasi fayli'
        verbose_name_plural = 'Diplom ilovasi fayllari'
        ordering = ['id']

    def __str__(self):
        return f"Diplom ilovasi #{self.id} - ariza #{self.application_id}"


class ApplicationPassportFile(BaseModel):
    application = models.ForeignKey(
        StudentApplication,
        related_name='passport_files',
        on_delete=models.CASCADE,
    )
    file = models.FileField(upload_to='admissions/passports/')

    class Meta:
        verbose_name = 'Passport fayli'
        verbose_name_plural = 'Passport fayllari'
        ordering = ['id']

    def __str__(self):
        return f"Passport #{self.id} - ariza #{self.application_id}"
