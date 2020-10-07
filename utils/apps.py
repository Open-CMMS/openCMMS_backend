from apscheduler.schedulers.background import BackgroundScheduler

from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = 'utils'

    def ready(self):
        from utils.notifications import start
        start()
