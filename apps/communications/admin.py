from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
from apps.common.admin_mixins import TranslationSafeAdminMixin
from .models import Contact, SocialLink, ContactAddress, ContactPhone, ContactEmail

class ContactAddressInline(TranslationTabularInline, TabularInline):
    model = ContactAddress
    extra = 1

class ContactPhoneInline(TabularInline):
    model = ContactPhone
    extra = 1

class ContactEmailInline(TabularInline):
    model = ContactEmail
    extra = 1

@admin.register(Contact)
class ContactAdmin(TranslationSafeAdminMixin, ModelAdmin, TabbedTranslationAdmin):
    list_display = ('address', 'phone', 'email')
    inlines = [ContactAddressInline, ContactPhoneInline, ContactEmailInline]
    ordering = ('-created_at',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

    def get_search_fields(self, request):
        translated_fields = tuple(f'address_{suffix}' for suffix in self.translation_suffixes)
        return ('address', 'phone', 'email') + translated_fields

@admin.register(SocialLink)
class SocialLinkAdmin(ModelAdmin):
    list_display = ('platform', 'url')
    search_fields = ('platform', 'url')
    ordering = ('platform',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')
