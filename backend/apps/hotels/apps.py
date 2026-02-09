from django.apps import AppConfig


class HotelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hotels'
    verbose_name = 'Hotels'

    def ready(self):
        """Import signal handlers when the app is ready."""
        try:
            import apps.hotels.signals  # noqa: F401
        except ImportError:
            pass
