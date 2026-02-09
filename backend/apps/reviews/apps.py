from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reviews'
    verbose_name = 'Reviews'

    def ready(self):
        """Import signal handlers when the app is ready."""
        try:
            import apps.reviews.signals  # noqa: F401
        except ImportError:
            pass
