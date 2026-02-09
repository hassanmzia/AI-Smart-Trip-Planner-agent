from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    label = 'users'
    verbose_name = 'Users'

    def ready(self):
        """Import signal handlers when the app is ready."""
        try:
            import apps.users.signals  # noqa: F401
        except ImportError:
            pass
