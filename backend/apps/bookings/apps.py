from django.apps import AppConfig


class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bookings'
    verbose_name = 'Bookings'

    def ready(self):
        """Import signal handlers when the app is ready."""
        try:
            import apps.bookings.signals  # noqa: F401
        except ImportError:
            pass
