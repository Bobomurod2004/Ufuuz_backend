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
        verbose_name="Ko'rib chiqish izohi",
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ko'rib chiqilgan vaqt",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='reviewed_student_applications',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Ko'rib chiqqan xodim",
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
            f"{self.last_name} {self.first_name} "
            f"({self.passport_series}{self.passport_number})"
        )


class _BaseDocument(BaseModel):
    file = models.FileField()

    class Meta:
        abstract = True
        ordering = ['id']


class ApplicationCV(_BaseDocument):
    application = models.ForeignKey(
        StudentApplication,
        related_name='cvs',
        on_delete=models.CASCADE,
        verbose_name='Ariza',
    )
    file = models.FileField(upload_to='admissions/cvs/', verbose_name='Fayl')

    class Meta(_BaseDocument.Meta):
        verbose_name = 'Tarjima hol'
        verbose_name_plural = 'Tarjima hollar'

    def __str__(self):
        return f"Tarjima hol #{self.id} – ariza #{self.application_id}"


class ApplicationMotivationLetter(_BaseDocument):
    application = models.ForeignKey(
        StudentApplication,
        related_name='motivation_letters',
        on_delete=models.CASCADE,
        verbose_name='Ariza',
    )
    file = models.FileField(
        upload_to='admissions/motivation_letters/',
        verbose_name='Fayl',
    )

    class Meta(_BaseDocument.Meta):
        verbose_name = 'Motivatsion xat'
        verbose_name_plural = 'Motivatsion xatlar'

    def __str__(self):
        return f"Motivatsion xat #{self.id} – ariza #{self.application_id}"


class ApplicationIdentityDocument(_BaseDocument):
    application = models.ForeignKey(
        StudentApplication,
        related_name='identity_documents',
        on_delete=models.CASCADE,
        verbose_name='Ariza',
    )
    file = models.FileField(
        upload_to='admissions/identity_documents/',
        verbose_name='Fayl',
    )

    class Meta(_BaseDocument.Meta):
        verbose_name = "Shaxsni tasdiqlovchi hujjat"
        verbose_name_plural = "Shaxsni tasdiqlovchi hujjatlar"

    def __str__(self):
        return f"Shaxs hujjati #{self.id} – ariza #{self.application_id}"


class ApplicationLanguageCertificate(_BaseDocument):
    application = models.ForeignKey(
        StudentApplication,
        related_name='language_certificates',
        on_delete=models.CASCADE,
        verbose_name='Ariza',
    )
    file = models.FileField(
        upload_to='admissions/language_certificates/',
        verbose_name='Fayl',
    )

    class Meta(_BaseDocument.Meta):
        verbose_name = 'Til sertifikati'
        verbose_name_plural = 'Til sertifikatlari'

    def __str__(self):
        return f"Til sertifikati #{self.id} – ariza #{self.application_id}"


class ApplicationTranscript(_BaseDocument):
    application = models.ForeignKey(
        StudentApplication,
        related_name='transcripts',
        on_delete=models.CASCADE,
        verbose_name='Ariza',
    )
    file = models.FileField(
        upload_to='admissions/transcripts/',
        verbose_name='Fayl',
    )

    class Meta(_BaseDocument.Meta):
        verbose_name = 'Baholar varaqasi'
        verbose_name_plural = 'Baholar varaqlari'

    def __str__(self):
        return f"Baholar varaqasi #{self.id} – ariza #{self.application_id}"


class ApplicationDiploma(_BaseDocument):
    application = models.ForeignKey(
        StudentApplication,
        related_name='diplomas',
        on_delete=models.CASCADE,
        verbose_name='Ariza',
    )
    file = models.FileField(
        upload_to='admissions/diplomas/',
        verbose_name='Fayl',
    )

    class Meta(_BaseDocument.Meta):
        verbose_name = 'Universitet diplomi'
        verbose_name_plural = 'Universitet diplomlari'

    def __str__(self):
        return f"Diplom #{self.id} – ariza #{self.application_id}"
