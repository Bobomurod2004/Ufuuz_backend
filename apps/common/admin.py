from django.contrib import admin
from unfold.admin import ModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from apps.common.admin_mixins import TranslationSafeAdminMixin
from .models import History, StaticPage

admin.site.site_header = "UFU boshqaruv paneli"
admin.site.site_title = "UFU Admin"
admin.site.index_title = "Ma'lumotlarni boshqarish"

@admin.register(History)
class HistoryAdmin(TranslationSafeAdminMixin, ModelAdmin, TabbedTranslationAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'title_uz', 'title_en', 'title_fr')
    ordering = ('-created_at',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

@admin.register(StaticPage)
class StaticPageAdmin(TranslationSafeAdminMixin, ModelAdmin, TabbedTranslationAdmin):
    list_display = ('title', 'slug')
    search_fields = ('title', 'slug', 'title_uz', 'title_en', 'title_fr')
    ordering = ('title',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {"slug": ("title",)}
