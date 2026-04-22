from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline
from modeltranslation.admin import TabbedTranslationAdmin
from apps.common.admin_mixins import TranslationSafeAdminMixin
from .models import (
    History,
    SliderCategory,
    SliderItem,
    StaticPage,
)

admin.site.site_header = "UFU boshqaruv paneli"
admin.site.site_title = "UFU Admin"
admin.site.index_title = "Ma'lumotlarni boshqarish"


@admin.register(History)
class HistoryAdmin(
    TranslationSafeAdminMixin,
    ModelAdmin,
    TabbedTranslationAdmin,
):
    list_display = ('title', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

    def get_search_fields(self, request):
        translated_fields = tuple(
            f'title_{suffix}' for suffix in self.translation_suffixes
        )
        return ('title',) + translated_fields


@admin.register(StaticPage)
class StaticPageAdmin(
    TranslationSafeAdminMixin,
    ModelAdmin,
    TabbedTranslationAdmin,
):
    list_display = ('title', 'slug')
    ordering = ('title',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

    def get_search_fields(self, request):
        translated_title_fields = tuple(
            f'title_{suffix}' for suffix in self.translation_suffixes
        )
        translated_slug_fields = tuple(
            f'slug_{suffix}' for suffix in self.translation_suffixes
        )
        return (
            'title',
            'slug',
            *translated_title_fields,
            *translated_slug_fields,
        )


class SliderItemInline(StackedInline):
    model = SliderItem
    extra = 1
    fields = (
        'category',
        'title',
        'title_uz',
        'title_en',
        'title_fr',
        'description',
        'description_uz',
        'description_en',
        'description_fr',
        'image',
        'video',
        'is_active',
        'order',
    )
    ordering = ('order',)


@admin.register(SliderCategory)
class SliderCategoryAdmin(
    TranslationSafeAdminMixin,
    ModelAdmin,
    TabbedTranslationAdmin,
):
    list_display = ('name', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at')
    ordering = ('order', 'id')
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'name_uz', 'name_en', 'name_fr')
        }),
        ('Status', {
            'fields': ('is_active', 'order')
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_search_fields(self, request):
        translated_fields = tuple(
            f'name_{suffix}' for suffix in self.translation_suffixes
        )
        return ('name',) + translated_fields


@admin.register(SliderItem)
class SliderItemAdmin(
    TranslationSafeAdminMixin,
    ModelAdmin,
    TabbedTranslationAdmin,
):
    list_display = (
        'get_title',
        'category',
        'is_active',
        'order',
        'created_at',
    )
    list_filter = ('is_active', 'category', 'created_at')
    ordering = ('category', 'order')
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')
    search_fields = (
        'title',
        'title_uz',
        'title_en',
        'title_fr',
        'description',
        'description_uz',
        'description_en',
        'description_fr',
        'category__name',
        'category__name_uz',
        'category__name_en',
        'category__name_fr',
    )
    fieldsets = (
        ('Kategoriya va sarlavha', {
            'fields': ('category', 'title', 'title_uz', 'title_en', 'title_fr')
        }),
        ('Tavsif', {
            'fields': ('description', 'description_uz', 'description_en', 'description_fr'),
            'classes': ('wide',)
        }),
        ('Media', {
            'fields': ('image', 'video'),
            'description': 'Rasm va video fayllarini yuklang'
        }),
        ('Tartib va Status', {
            'fields': ('order', 'is_active')
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_title(self, obj):
        return obj.title[:50] if obj.title else 'Sarlavhasiz'
    get_title.short_description = 'Sarlavha'

    def get_search_fields(self, request):
        translated_fields = []
        for base_field in ('title', 'description'):
            translated_fields.extend(
                f'{base_field}_{suffix}'
                for suffix in self.translation_suffixes
            )
        return (
            'category',
            'title',
            'description',
            *translated_fields,
        )
