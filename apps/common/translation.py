from modeltranslation.translator import register, TranslationOptions
from .models import History, StaticPage, Slider, SliderItem

@register(History)
class HistoryTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

@register(StaticPage)
class StaticPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

@register(Slider)
class SliderTranslationOptions(TranslationOptions):
    fields = ('title',)

@register(SliderItem)
class SliderItemTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
