from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    ApplicationCertificate,
    ApplicationDiploma,
    ApplicationDiplomaSupplement,
    ApplicationPassportFile,
    ApplicationPdf,
    StudentApplication,
)


class ApplicationDiplomaInline(TabularInline):
    model = ApplicationDiploma
    extra = 0
    fields = ('file', 'created_at', 'updated_at')
    readonly_fields = ('file', 'created_at', 'updated_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and user.is_active and user.is_staff)


class ApplicationCertificateInline(TabularInline):
    model = ApplicationCertificate
    extra = 0
    fields = ('file', 'created_at', 'updated_at')
    readonly_fields = ('file', 'created_at', 'updated_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and user.is_active and user.is_staff)


class ApplicationPdfInline(TabularInline):
    model = ApplicationPdf
    extra = 0
    fields = ('file', 'created_at', 'updated_at')
    readonly_fields = ('file', 'created_at', 'updated_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and user.is_active and user.is_staff)


class ApplicationDiplomaSupplementInline(TabularInline):
    model = ApplicationDiplomaSupplement
    extra = 0
    fields = ('file', 'created_at', 'updated_at')
    readonly_fields = ('file', 'created_at', 'updated_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and user.is_active and user.is_staff)


class ApplicationPassportFileInline(TabularInline):
    model = ApplicationPassportFile
    extra = 0
    fields = ('file', 'created_at', 'updated_at')
    readonly_fields = ('file', 'created_at', 'updated_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and user.is_active and user.is_staff)


@admin.register(StudentApplication)
class StudentApplicationAdmin(ModelAdmin):
    list_display = (
        'id',
        'last_name',
        'first_name',
        'middle_name',
        'passport_series',
        'passport_number',
        'phone_number',
        'created_at',
    )
    list_filter = ('created_at',)
    search_fields = (
        'first_name',
        'last_name',
        'middle_name',
        'passport_series',
        'passport_number',
        'phone_number',
    )
    ordering = ('-created_at',)
    list_per_page = 20
    readonly_fields = (
        'first_name',
        'last_name',
        'middle_name',
        'passport_series',
        'passport_number',
        'phone_number',
        'status',
        'review_note',
        'reviewed_by',
        'reviewed_at',
        'created_at',
        'updated_at',
    )
    inlines = [
        ApplicationPdfInline,
        ApplicationDiplomaSupplementInline,
        ApplicationPassportFileInline,
        ApplicationDiplomaInline,
        ApplicationCertificateInline,
    ]
    fieldsets = (
        ("Ariza ma'lumotlari", {
            'fields': (
                'first_name',
                'last_name',
                'middle_name',
                'passport_series',
                'passport_number',
                'phone_number',
            ),
        }),
        ('Holat ma\'lumotlari', {
            'fields': (
                'status',
                'review_note',
                'reviewed_by',
                'reviewed_at',
            ),
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def _can_access(self, request):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and user.is_active and user.is_staff)

    def has_module_permission(self, request):
        return self._can_access(request)

    def has_view_permission(self, request, obj=None):
        return self._can_access(request)

    def has_change_permission(self, request, obj=None):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and user.is_superuser)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and user.is_superuser)
