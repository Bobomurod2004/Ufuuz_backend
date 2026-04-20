from modeltranslation.translator import TranslationOptions, register

from .models import History, SliderCategory, SliderItem, StaticPage


@register(History)
class HistoryTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


@register(StaticPage)
class StaticPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


@register(SliderItem)
class SliderItemTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(SliderCategory)
class SliderCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
