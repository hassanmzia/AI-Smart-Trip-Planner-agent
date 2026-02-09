from django.apps import AppConfig


class AttractionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.attractions'
    verbose_name = 'Attractions'

    def ready(self):
        """Import signal handlers when the app is ready."""
        try:
            import apps.attractions.signals  # noqa: F401
        except ImportError:
            pass
