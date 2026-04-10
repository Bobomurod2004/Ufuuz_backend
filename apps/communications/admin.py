from django.contrib import admin
from unfold.admin import ModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from apps.common.admin_mixins import TranslationSafeAdminMixin
from .models import Contact, SocialLink

@admin.register(Contact)
class ContactAdmin(TranslationSafeAdminMixin, ModelAdmin, TabbedTranslationAdmin):
    list_display = ('address', 'phone', 'email')
    search_fields = ('address', 'phone', 'email', 'address_uz', 'address_en', 'address_fr')
    ordering = ('-created_at',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SocialLink)
class SocialLinkAdmin(ModelAdmin):
    list_display = ('platform', 'url')
    search_fields = ('platform', 'url')
    ordering = ('platform',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')
