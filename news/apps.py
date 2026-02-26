"""
Application configuration for the News app.
This module handles app initialization and ensures that Django signals
are properly registered when the application starts.
"""

from django.apps import AppConfig


class NewsConfig(AppConfig):
    """
    Configuration class for the News application.
    Sets the default primary key type and triggers signal registration.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "news"

    def ready(self):
        """
        Override the ready method to import signals.
        This is necessary to ensure signal handlers are connected
        when the application registry is fully populated.
        """

        import news.signals   # noqa This connects the signal logic
