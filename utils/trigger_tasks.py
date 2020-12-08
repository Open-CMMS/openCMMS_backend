"""This file allows to trigger tasks with trigger condition."""

import logging
from maintenancemanagement.models import Field, FieldGroup, FieldObject, Task

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

def check_tasks():
    tasks_to_check = Task.objects.filter(over=False, is_activated=False)
    for task in tasks_to_check:
        if at_least_one_conditon_is_verified(task):
            task.is_activated = True
            task.save()

def at_least_one_conditon_is_verified(task):
    trigger_conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="Trigger Conditions"))
    task_conditions = FieldObject.objects.filter(field__in=trigger_conditions, described_object=task)
    for condition in task_conditions:
        if condition_is_verified(condition) is True:
            return True
    return False

def condition_is_verified(condition):
    pass
    # A CODER

def start():
    r"""\n# Set up the cron job to trigger tasks."""
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(check_tasks, 'cron', day_of_week='mon-fri', hour='6', minute='30')
        scheduler.start()
    except Exception as e:
        logger.critical("The trigger tasks scheduler did not start. {}", e)