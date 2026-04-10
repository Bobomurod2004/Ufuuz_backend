from django import forms


class AutoPopulateTranslationFieldsForm(forms.ModelForm):
    translation_suffixes = ('uz', 'en', 'fr')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self._is_translation_field(field_name):
                field.required = False

    def clean(self):
        cleaned_data = super().clean()
        for field_name in list(cleaned_data.keys()):
            if not self._is_translation_field(field_name):
                continue

            base_name = self._base_field_name(field_name)
            translated_value = cleaned_data.get(field_name)
            base_value = cleaned_data.get(base_name)

            if not translated_value and base_value:
                cleaned_data[field_name] = base_value

        return cleaned_data

    def _is_translation_field(self, field_name: str) -> bool:
        return any(field_name.endswith(f'_{suffix}') for suffix in self.translation_suffixes)

    def _base_field_name(self, field_name: str) -> str:
        return field_name.rsplit('_', 1)[0]
