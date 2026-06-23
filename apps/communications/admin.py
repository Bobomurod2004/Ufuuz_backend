from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
from apps.common.admin_mixins import (
    SuperuserOnlyAdminMixin,
    TranslationSafeAdminMixin,
)
from .models import Contact, SocialLink, ContactAddress, ContactPhone, ContactEmail


class ContactAddressInline(TranslationTabularInline):
    model = ContactAddress
    extra = 1


class ContactPhoneInline(admin.TabularInline):
    model = ContactPhone
    extra = 1


class ContactEmailInline(admin.TabularInline):
    model = ContactEmail
    extra = 1


@admin.register(Contact)
class ContactAdmin(
    SuperuserOnlyAdminMixin,
    TranslationSafeAdminMixin,
    TabbedTranslationAdmin,
):
    list_display = ('address', 'phone', 'email')
    inlines = [ContactAddressInline, ContactPhoneInline, ContactEmailInline]
    ordering = ('-created_at',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

    def get_search_fields(self, request):
        translated = tuple(
            f'address_{s}' for s in self.translation_suffixes
        )
        return ('address', 'phone', 'email') + translated


@admin.register(SocialLink)
class SocialLinkAdmin(SuperuserOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('platform', 'url')
    search_fields = ('platform', 'url')
    ordering = ('platform',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')
