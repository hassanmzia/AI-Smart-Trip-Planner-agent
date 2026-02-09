from django.apps import AppConfig


class RestaurantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.restaurants'
    verbose_name = 'Restaurants'

    def ready(self):
        """Import signal handlers when the app is ready."""
        try:
            import apps.restaurants.signals  # noqa: F401
        except ImportError:
            pass
