"""This script describes our utils app."""
import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


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
        except Exception as e:
            logger.critical("The schedulers ran into a problem.{}", e)
