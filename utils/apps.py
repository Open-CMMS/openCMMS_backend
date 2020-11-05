from django.apps import AppConfig
import sys

class UtilsConfig(AppConfig):
    name = 'utils'

    def ready(self):
        if 'pytest' not in sys.argv[0]:
            from utils import notifications
            notifications.start()
            from utils import data_provider
            data_provider.start()
