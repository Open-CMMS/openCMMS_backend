"""This script describes our utils app."""
from django.apps import AppConfig


class UtilsConfig(AppConfig):
    """The app class."""

    name = 'utils'

    def ready(self):
        """Launch our APSchedulers for our background tasks."""
        try:
            from utils import notifications
            notifications.start()
            from utils import data_provider
            data_provider.start()
        except Exception:
            pass
