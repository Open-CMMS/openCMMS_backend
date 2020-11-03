"""This is our script that execute all the get_data methods"""
import importlib
from os import chdir, listdir, path

from apscheduler.schedulers.background import BackgroundScheduler

from maintenancemanagement.models import FieldObject
from openCMMS.settings import BASE_DIR
from utils.models import Plugin

scheduler = BackgroundScheduler()
scheduler.start()


def main():
    plugins = Plugin.objects.filter(is_activated=True)
    for plugin in plugins:
        recurrence = recurrence_to_cron(plugin.recurrence)
        scheduler.add_job(
            func=trigger_plugin,
            trigger='cron',
            kwargs={"plugin": plugin},
        )


def trigger_plugin(plugin):
    module = importlib.import_module(f"utils.data_providers.{plugin.file_name[:-3]}")
    field = FieldObject.objects.get(id=plugin.field_object)
    field.value = module.get_data(plugin.ip_address)
    field.save()


def recurrence_to_cron(reccurence):
    pass
