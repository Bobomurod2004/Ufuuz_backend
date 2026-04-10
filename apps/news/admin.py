from django.contrib import admin
from unfold.admin import ModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from apps.common.admin_forms import AutoPopulateTranslationFieldsForm
from .models import Category, News

@admin.register(Category)
class CategoryAdmin(ModelAdmin, TabbedTranslationAdmin):
    form = AutoPopulateTranslationFieldsForm
    list_display = ('title',)
    search_fields = ('title', 'title_uz', 'title_en', 'title_fr')
    ordering = ('title',)
    list_per_page = 20

@admin.register(News)
class NewsAdmin(ModelAdmin, TabbedTranslationAdmin):
    form = AutoPopulateTranslationFieldsForm
    list_display = ('title', 'category', 'is_published', 'created_at')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'slug', 'summary', 'title_uz', 'title_en', 'title_fr')
    ordering = ('-created_at',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {"slug": ("title",)}
