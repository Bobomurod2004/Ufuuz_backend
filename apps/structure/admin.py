from django.contrib import admin
from unfold.admin import ModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from apps.common.admin_mixins import TranslationSafeAdminMixin
from .models import Faculty, Department

@admin.register(Faculty)
class FacultyAdmin(TranslationSafeAdminMixin, ModelAdmin, TabbedTranslationAdmin):
    list_display = ('title', 'created_at')
    ordering = ('title',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

    def get_search_fields(self, request):
        translated_fields = tuple(f'title_{suffix}' for suffix in self.translation_suffixes)
        return ('title', 'description') + translated_fields

@admin.register(Department)
class DepartmentAdmin(TranslationSafeAdminMixin, ModelAdmin, TabbedTranslationAdmin):
    list_display = ('title', 'faculty', 'head_name')
    list_filter = ('faculty',)
    ordering = ('title',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

    def get_search_fields(self, request):
        translated_fields = tuple(f'title_{suffix}' for suffix in self.translation_suffixes)
        return ('title', 'head_name', 'contact_info') + translated_fields
