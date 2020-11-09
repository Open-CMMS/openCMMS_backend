import sys

from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = 'utils'

    def ready(self):
        try:
            from utils import notifications
            notifications.start()
            from utils import data_provider
            data_provider.start()
        except:
            pass
