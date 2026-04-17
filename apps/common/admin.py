from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline
from modeltranslation.admin import TabbedTranslationAdmin
from apps.common.admin_mixins import TranslationSafeAdminMixin
from .models import History, StaticPage, Slider, SliderItem

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
        translated_fields = tuple(f'title_{suffix}' for suffix in self.translation_suffixes)
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
    prepopulated_fields = {"slug": ("title",)}

    def get_search_fields(self, request):
        translated_fields = tuple(f'title_{suffix}' for suffix in self.translation_suffixes)
        return ('title', 'slug') + translated_fields


class SliderItemInline(StackedInline):
    model = SliderItem
    extra = 1
    fields = ('title', 'image', 'link', 'order')
    ordering = ('order',)


@admin.register(Slider)
class SliderAdmin(ModelAdmin):
    list_display = ('title', 'is_active', 'order')
    search_fields = ('title',)
    ordering = ('order',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SliderItemInline]
    list_filter = ('is_active',)
