from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from apps.common.admin_mixins import (
    SuperuserOnlyAdminMixin,
    TranslationSafeAdminMixin,
)
from .models import Faculty, Department


@admin.register(Faculty)
class FacultyAdmin(
    SuperuserOnlyAdminMixin,
    TranslationSafeAdminMixin,
    TabbedTranslationAdmin,
):
    list_display = ('title', 'created_at')
    ordering = ('title',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

    def get_search_fields(self, request):
        translated = tuple(
            f'title_{s}' for s in self.translation_suffixes
        )
        return ('title', 'description') + translated


@admin.register(Department)
class DepartmentAdmin(
    SuperuserOnlyAdminMixin,
    TranslationSafeAdminMixin,
    TabbedTranslationAdmin,
):
    list_display = ('title', 'faculty', 'head_name')
    list_filter = ('faculty',)
    ordering = ('title',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

    def get_search_fields(self, request):
        translated = tuple(
            f'title_{s}' for s in self.translation_suffixes
        )
        return ('title', 'head_name', 'contact_info') + translated
