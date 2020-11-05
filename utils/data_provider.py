"""This is our script that execute all the get_data methods."""
import importlib
import re
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from maintenancemanagement.models import FieldObject
from utils.models import DataProvider

scheduler = BackgroundScheduler()
scheduler.start()


class GetDataException(Exception):
    """Exception corresponding to get_data method."""

    pass


class DataProviderException(Exception):
    """Exception corresponding to a DataProvider error."""

    pass


def start():
    """Initialise all data provider jobs when django starts."""
    print(DataProvider.objects.all())
    dataproviders = DataProvider.objects.filter(is_activated=True)
    for dataprovider in dataproviders:
        try:
            test_dataprovider_configuration(dataprovider.file_name, dataprovider.ip_address)
            add_job(dataprovider)
        except:
            pass
            # A CODER


def add_job(dataprovider):
    """Add a job for the given data provider."""
    recurrence = _parse_time(dataprovider.recurrence)
    if recurrence:
        hours = recurrence.seconds // 3600
        minutes = (recurrence.seconds - hours * 3600) // 60
        job = scheduler.add_job(
            _trigger_dataprovider,
            'interval',
            kwargs={"dataprovider": dataprovider},
            days=recurrence.days,
            hours=hours,
            minutes=minutes
        )
        dataprovider.job_id = job.id
        dataprovider.save()


def _trigger_dataprovider(dataprovider):
    """Update the indicated field from a data provider."""
    try:
        module = importlib.import_module(f"utils.data_providers.{dataprovider.file_name[:-3]}")
        field = FieldObject.objects.get(id=dataprovider.field_object)
        field.value = module.get_data(dataprovider.ip_address)
        field.save()
    except:
        pass
        # A CODER


def _parse_time(time_str):
    regex = re.compile(r'((?P<days>\d+?)d ?)?((?P<hours>\d+?)h ?)?((?P<minutes>\d+?)m ?)?')
    parts = regex.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)


def test_dataprovider_configuration(file_name, ip_address):
    """Trigger the get_data method and return the result or an error."""
    try:
        module = importlib.import_module(f"utils.data_providers.{file_name[:-3]}")
        return module.get_data(ip_address)
    except ModuleNotFoundError:
        raise DataProviderException("Python file not found, please enter 'name_of_your_file.py'")
    except AttributeError:
        raise DataProviderException('Python file is not well formated, please follow the example')
    except GetDataException:
        raise DataProviderException('IP not found or python file not working')
