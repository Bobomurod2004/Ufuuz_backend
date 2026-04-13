from django.apps import AppConfig
import inspect

class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.common'
    verbose_name = "Asosiy sahifalar"

    def ready(self):
        """Compatibility patch for old django-modeltranslation with Django 6."""
        try:
            from modeltranslation.manager import MultilingualQuerySet
        except Exception:
            return

        update_method = getattr(MultilingualQuerySet, '_update', None)
        if update_method is None:
            return

        # Old versions define: _update(self, values)
        # Django 6 calls: _update(self, values, returning_fields=None)
        params = list(inspect.signature(update_method).parameters.keys())
        if len(params) >= 3:
            return

        def _update_compat(self, values, returning_fields=None):
            return update_method(self, values)

        MultilingualQuerySet._update = _update_compat
