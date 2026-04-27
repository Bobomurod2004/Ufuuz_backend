from modeltranslation.translator import register, TranslationOptions
from .models import Contact, ContactAddress

@register(Contact)
class ContactTranslationOptions(TranslationOptions):
    fields = ('address', 'working_hours')

@register(ContactAddress)
class ContactAddressTranslationOptions(TranslationOptions):
    fields = ('address',)
