from django.apps import AppConfig


class AgentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.agents'
    verbose_name = 'AI Agents'

    def ready(self):
        """Import signal handlers when the app is ready."""
        try:
            import apps.agents.signals  # noqa: F401
        except ImportError:
            pass
