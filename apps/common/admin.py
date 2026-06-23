from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from apps.common.admin_mixins import (
    SuperuserOnlyAdminMixin,
    TranslationSafeAdminMixin,
)
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
    SuperuserOnlyAdminMixin,
    TranslationSafeAdminMixin,
    TabbedTranslationAdmin,
):
    list_display = ('title', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

    def get_search_fields(self, request):
        translated = tuple(
            f'title_{s}' for s in self.translation_suffixes
        )
        return ('title',) + translated


@admin.register(StaticPage)
class StaticPageAdmin(
    SuperuserOnlyAdminMixin,
    TranslationSafeAdminMixin,
    TabbedTranslationAdmin,
):
    list_display = ('title', 'slug')
    ordering = ('title',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

    def get_search_fields(self, request):
        title_fields = tuple(
            f'title_{s}' for s in self.translation_suffixes
        )
        slug_fields = tuple(
            f'slug_{s}' for s in self.translation_suffixes
        )
        return ('title', 'slug') + title_fields + slug_fields


class SliderItemInline(admin.StackedInline):
    model = SliderItem
    extra = 1
    fields = (
        'category',
        'title',
        'description',
        'image',
        'video',
        'is_active',
        'order',
    )
    ordering = ('order',)


@admin.register(SliderCategory)
class SliderCategoryAdmin(
    SuperuserOnlyAdminMixin,
    TranslationSafeAdminMixin,
    TabbedTranslationAdmin,
):
    list_display = ('name', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at')
    ordering = ('order', 'id')
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('name',),
        }),
        ('Status', {
            'fields': ('is_active', 'order'),
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_search_fields(self, request):
        translated = tuple(
            f'name_{s}' for s in self.translation_suffixes
        )
        return ('name',) + translated


@admin.register(SliderItem)
class SliderItemAdmin(
    SuperuserOnlyAdminMixin,
    TranslationSafeAdminMixin,
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
    search_fields = ('title', 'description', 'category__name')
    fieldsets = (
        ('Kategoriya va sarlavha', {
            'fields': ('category', 'title'),
        }),
        ('Tavsif', {
            'fields': ('description',),
            'classes': ('wide',),
        }),
        ('Media', {
            'fields': ('image', 'video'),
            'description': 'Rasm va video fayllarini yuklang',
        }),
        ('Tartib va Status', {
            'fields': ('order', 'is_active'),
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_title(self, obj):
        return obj.title[:50] if obj.title else 'Sarlavhasiz'
    get_title.short_description = 'Sarlavha'

    def get_search_fields(self, request):
        translated = []
        for base in ('title', 'description'):
            translated.extend(
                f'{base}_{s}' for s in self.translation_suffixes
            )
        return ('category', 'title', 'description') + tuple(translated)
