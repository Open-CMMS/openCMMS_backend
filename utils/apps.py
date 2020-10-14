from apscheduler.schedulers.background import BackgroundScheduler

from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = 'utils'

    def ready(self):
        """Start scheduler with listed jobs."""
        from utils.notifications import send_notifications
        from utils.triggers import activate_triggered_tasks

        scheduler = BackgroundScheduler()
        scheduler.add_job(send_notifications, 'cron', day_of_week='mon-fri', hour='6', minute='30')
        scheduler.add_job(activate_triggered_tasks, 'cron', day_of_week='mon-sun', hour='5')
        scheduler.start()
