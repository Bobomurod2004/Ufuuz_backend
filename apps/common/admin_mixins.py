from django.conf import settings


class TranslationSafeAdminMixin:
    translation_autofill_excluded_base_fields = ()

    @property
    def translation_suffixes(self):
        return tuple(code for code, _ in settings.LANGUAGES)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        default_language = getattr(settings, 'MODELTRANSLATION_DEFAULT_LANGUAGE', 'uz')
        for field_name, field in form.base_fields.items():
            if self._is_translation_field(field_name):
                # Ensure the default language field inherits the base field's required status
                if field_name.endswith(f'_{default_language}'):
                    base_field_name = self._base_field_name(field_name)
                    base_field = form.base_fields.get(base_field_name)
                    if base_field and base_field.required:
                        continue
                field.required = False
        return form

    def save_model(self, request, obj, form, change):
        for field_name in form.cleaned_data:
            if not self._is_translation_field(field_name):
                continue

            base_field_name = self._base_field_name(field_name)
            if self._is_autofill_excluded_field(base_field_name):
                continue
            translated_value = form.cleaned_data.get(field_name)
            base_value = form.cleaned_data.get(base_field_name)

            if not translated_value and base_value:
                setattr(obj, field_name, base_value)

        super().save_model(request, obj, form, change)

    def _is_autofill_excluded_field(self, base_field_name: str) -> bool:
        return base_field_name in self.translation_autofill_excluded_base_fields

    def _is_translation_field(self, field_name: str) -> bool:
        return any(field_name.endswith(f'_{suffix}') for suffix in self.translation_suffixes)

    def _base_field_name(self, field_name: str) -> str:
        return field_name.rsplit('_', 1)[0]
