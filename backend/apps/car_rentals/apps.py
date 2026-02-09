from django.apps import AppConfig


class CarRentalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.car_rentals'
    verbose_name = 'Car Rentals'

    def ready(self):
        """Import signal handlers when the app is ready."""
        try:
            import apps.car_rentals.signals  # noqa: F401
        except ImportError:
            pass
