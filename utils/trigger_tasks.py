"""This file allows to trigger tasks with trigger condition."""

import logging
from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler

from maintenancemanagement.models import Field, FieldGroup, FieldObject, Task
from utils.methods import parse_time

logger = logging.getLogger(__name__)


def check_tasks():
    tasks_to_check = Task.objects.filter(over=False, is_activated=False)
    for task in tasks_to_check:
        condition = at_least_one_conditon_is_verified(task)
        if condition:
            task.is_activated = True
            if condition.field.name in ['Above Threshold', 'Under Threshold', 'Frequency']:
                task.end_date = date.today() + parse_time(condition.value.split('|')[2])
            task.save()


def at_least_one_conditon_is_verified(task):
    content_type_object = ContentType.objects.get_for_model(task)
    task_conditions = FieldObject.objects.filter(
        object_id=task.id,
        content_type=content_type_object,
        field__field_group__name='Trigger Conditions',
    )
    for condition in task_conditions:
        if condition_is_verified(condition, task):
            return condition
    return None


def condition_is_verified(condition, task):
    """Check if the condition given is validated to activate the given task."""
    if condition.field.name == 'Recurrence':
        delay = condition.value.split('|')[1]
        return date.today() > task.end_date - parse_time(delay)
    elif condition.field.name == 'Frequency':
        field_object_id = int(condition.value.split('|')[1])
        value = float(FieldObject.objects.get(id=field_object_id).value)
        next_trigger = float(condition.value.split('|')[3])
        return value > next_trigger
    else:
        field_object_id = int(condition.value.split('|')[1])
        value = float(FieldObject.objects.get(id=field_object_id).value)
        threshold = float(condition.value.split('|')[0])
        if condition.field.name == 'Above Threshold':
            return threshold < value
        if condition.field.name == 'Under Threshold':
            return threshold > value


def start():
    r"""\n# Set up the cron job to trigger tasks."""
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(check_tasks, 'cron', day_of_week='mon-fri', hour='6', minute='30')
        scheduler.start()
    except Exception as e:
        logger.critical("The trigger tasks scheduler did not start. {}", e)
