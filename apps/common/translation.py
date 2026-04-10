from modeltranslation.translator import register, TranslationOptions
from .models import History, StaticPage

@register(History)
class HistoryTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

@register(StaticPage)
class StaticPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content')
