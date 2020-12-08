"""This is our script that execute all the get_data methods."""
import importlib
import logging
import re

from apscheduler.schedulers.background import BackgroundScheduler

from django.core.exceptions import ObjectDoesNotExist
from maintenancemanagement.models import FieldObject
from utils.models import DataProvider

scheduler = BackgroundScheduler()
scheduler.start()

logger = logging.getLogger(__name__)


class GetDataException(Exception):
    """Exception corresponding to get_data method."""

    pass


class DataProviderException(Exception):
    """Exception corresponding to a DataProvider error."""

    pass


def start():
    """Initialise all data provider jobs when django starts."""
    dataproviders = DataProvider.objects.filter()
    for dataprovider in dataproviders:
        add_job(dataprovider)
        try:
            test_dataprovider_configuration(dataprovider.file_name, dataprovider.ip_address, dataprovider.port)
        except Exception as e:
            dataprovider.is_activated = None
            dataprovider.save()
            logger.warning("The data provider '{}' doesn't work : {}".format(dataprovider.name, e))


def add_job(dataprovider):
    """Add a job for the given data provider."""
    recurrence = _parse_time(dataprovider.recurrence)
    if recurrence:
        job = scheduler.add_job(
            _trigger_dataprovider,
            'interval',
            kwargs={"dataprovider": dataprovider},
            days=recurrence["days"],
            hours=recurrence["hours"],
            minutes=recurrence["minutes"]
        )
        dataprovider.job_id = job.id
        dataprovider.save()
        if dataprovider.is_activated is False:
            scheduler.pause_job(dataprovider.job_id)


def _trigger_dataprovider(dataprovider):
    """Update the indicated field from a data provider."""
    module = ""
    try:
        module = importlib.import_module(f"utils.data_providers.{dataprovider.file_name[:-3]}")
        field = FieldObject.objects.get(id=dataprovider.field_object.id)
        value = module.get_data(dataprovider.ip_address, dataprovider.port)
        logger.info("FieldObject '{}' UPDATED with value : {}".format(repr(field), value))
        field.value = value
        field.save()
        dataprovider.is_activated = True
        dataprovider.save()
    except ImportError:
        dataprovider.is_activated = None
        dataprovider.save()
        logger.warning(
            "The dataProvider {filename} could not be imported.\n{}".format(
                ImportError, filename=dataprovider.file_name
            )
        )
    except ObjectDoesNotExist:
        dataprovider.is_activated = None
        dataprovider.save()
        logger.warning(
            "The field {field} was not found.\n{}".format(ObjectDoesNotExist, field=dataprovider.field_object)
        )
    except GetDataException:
        dataprovider.is_activated = None
        dataprovider.save()
        logger.warning(
            "The execution of get_data of the module {module} run into an error.\n{}".format(
                GetDataException, module=module
            )
        )


def _parse_time(time_str):
    regex = re.compile(r'((?P<days>\d+?)d ?)?((?P<hours>\d+?)h ?)?((?P<minutes>\d+?)m ?)?')
    parts = regex.match(time_str)
    res = {}
    for (key, value) in parts.groupdict().items():
        if value:
            res[key] = int(value)
        else:
            res[key] = 0
    return res


def test_dataprovider_configuration(file_name, ip_address, port):
    """Trigger the get_data method and return the result or an error."""
    try:
        module = importlib.import_module(f"utils.data_providers.{file_name[:-3]}")
        return module.get_data(ip_address, port)
    except ModuleNotFoundError:
        raise DataProviderException("Python file not found, please enter 'name_of_your_file.py'")
    except AttributeError:
        raise DataProviderException('Python file is not well formated, please follow the example')
    except GetDataException:
        raise DataProviderException('IP not found or python file not working')
