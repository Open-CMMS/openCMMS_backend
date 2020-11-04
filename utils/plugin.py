"""This is our script that execute all the get_data methods"""
import importlib
from os import chdir, listdir, path

from apscheduler.schedulers.background import BackgroundScheduler

from maintenancemanagement.models import FieldObject
from openCMMS.settings import BASE_DIR
from utils.models import DataProvider

scheduler = BackgroundScheduler()
scheduler.start()


def main():
    dataproviders = DataProvider.objects.filter(is_activated=True)
    for dataprovider in dataproviders:
        recurrence = recurrence_to_cron(dataprovider.recurrence)
        scheduler.add_job(
            func=trigger_dataprovider,
            trigger='cron',
            kwargs={"dataprovider": dataprovider},
        )


def trigger_dataprovider(dataprovider):
    module = importlib.import_module(f"utils.data_providers.{dataprovider.file_name[:-3]}")
    field = FieldObject.objects.get(id=dataprovider.field_object)
    field.value = module.get_data(dataprovider.ip_address)
    field.save()


def recurrence_to_cron(reccurence):
    pass
