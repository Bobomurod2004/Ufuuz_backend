from django.contrib import admin
from unfold.admin import ModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from .models import Faculty, Department

@admin.register(Faculty)
class FacultyAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description', 'title_uz', 'title_en', 'title_fr')
    ordering = ('title',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Department)
class DepartmentAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ('title', 'faculty', 'head_name')
    list_filter = ('faculty',)
    search_fields = ('title', 'head_name', 'contact_info', 'title_uz', 'title_en', 'title_fr')
    ordering = ('title',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')
