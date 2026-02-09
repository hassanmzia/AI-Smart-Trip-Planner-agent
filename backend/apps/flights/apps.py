from django.apps import AppConfig


class FlightsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.flights'
    verbose_name = 'Flights'

    def ready(self):
        """Import signal handlers when the app is ready."""
        try:
            import apps.flights.signals  # noqa: F401
        except ImportError:
            pass
