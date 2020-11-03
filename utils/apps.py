from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = 'utils'

    def ready(self):
        from utils.notifications import start
        start()
        from utils.plugin import main

        # main()
