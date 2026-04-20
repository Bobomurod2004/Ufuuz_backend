from modeltranslation.translator import register, TranslationOptions
from .models import Category, News, NewsImage, NewsVideo

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('title',)

@register(News)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'summary', 'content')


@register(NewsImage)
class NewsImageTranslationOptions(TranslationOptions):
    fields = ('caption',)


@register(NewsVideo)
class NewsVideoTranslationOptions(TranslationOptions):
    fields = ('title',)
