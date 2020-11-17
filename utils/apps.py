"""This script describes our utils app."""
from logging import getLogger

from django.apps import AppConfig

logger = getLogger(__name__)


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
            logger.critical("The crons could not be started.\n{}", e)
