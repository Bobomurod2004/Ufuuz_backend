from django.contrib import admin
from unfold.admin import ModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from apps.common.admin_mixins import TranslationSafeAdminMixin
from .models import Category, News, NewsImage, NewsVideo


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1
    fields = ('image', 'caption', 'order', 'is_active')


class NewsVideoInline(admin.TabularInline):
    model = NewsVideo
    extra = 1
    fields = ('title', 'video', 'video_url', 'preview_image', 'order', 'is_active')

@admin.register(Category)
class CategoryAdmin(TranslationSafeAdminMixin, ModelAdmin, TabbedTranslationAdmin):
    list_display = ('id', 'title')
    ordering = ('title',)
    list_per_page = 20

    def get_search_fields(self, request):
        translated_fields = tuple(f'title_{suffix}' for suffix in self.translation_suffixes)
        return ('title',) + translated_fields


@admin.register(News)
class NewsAdmin(TranslationSafeAdminMixin, ModelAdmin, TabbedTranslationAdmin):
    list_display = ('id', 'title', 'category', 'published_at', 'is_published', 'created_at')
    list_filter = ('category', 'is_published', 'published_at')
    ordering = ('-published_at', '-created_at')
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'published_at'
    inlines = [NewsImageInline, NewsVideoInline]
    translation_autofill_excluded_base_fields = ('slug',)

    def get_search_fields(self, request):
        slug_fields = tuple(f'slug_{suffix}' for suffix in self.translation_suffixes)
        title_fields = tuple(f'title_{suffix}' for suffix in self.translation_suffixes)
        summary_fields = tuple(f'summary_{suffix}' for suffix in self.translation_suffixes)
        return ('title', 'slug', 'summary') + slug_fields + title_fields + summary_fields
