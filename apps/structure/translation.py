from modeltranslation.translator import register, TranslationOptions
from .models import Faculty, Department

@register(Faculty)
class FacultyTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(Department)
class DepartmentTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
