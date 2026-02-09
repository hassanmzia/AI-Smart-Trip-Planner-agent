from django.apps import AppConfig


class ItinerariesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.itineraries'
    verbose_name = 'Itineraries'

    def ready(self):
        """Import signal handlers when the app is ready."""
        try:
            import apps.itineraries.signals  # noqa: F401
        except ImportError:
            pass
