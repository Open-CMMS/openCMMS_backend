from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = 'utils'

    def ready(self):
        from utils.notifications import start
        start()
        # from utils.dataprovider import main
        # main()
