"""This file allows to send email notifications."""

from datetime import date, timedelta

from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from maintenancemanagement.models import Task
from usersmanagement.models import UserProfile


def send_notifications():
    r"""\n# Send notifications to users who have late or imminent tasks."""
    for user in UserProfile.objects.all():
        template = get_notification_template(user)
        if template:
            plain_message = strip_tags(template)
            mail.send_mail(
                'Notification Open-CMMS', plain_message, settings.EMAIL_HOST_USER, [user.email], html_message=template
            )


def get_notification_template(user):
    r"""\n# Get notification template for a user.

    Parameter :
    user (UserProfile) : the user for whom we wish to obtain the template.

    Return :
    notifictaion-template (String) : the template.
    OR
    None : if the user has no imminent tasks
    """
    tasks = get_imminent_tasks(user)
    if len(tasks[0]) + len(tasks[1]) + len(tasks[2]) > 0:
        return render_to_string('notification_mail.html', {'tasks': tasks, 'base_url': settings.BASE_URL})
    return None


def get_imminent_tasks(user):
    r"""\n# Get late, today and coming tasks for a user.

    Parameter :
    user (UserProfile) : the user for whom we wish to obtain the late\
         and imminent tasks.

    Return :
    tuple_of_sets_of_tasks ((late_tasks_set(), today_tasks_set(), \
        coming_tasks_set())) : the tasks assigned to the user.
    """
    result = (set(), set(), set())
    tasks = Task.objects.filter(teams__pk__in=user.groups.all().values_list("id", flat=True).iterator(), over=False)
    for task in tasks:
        if task.end_date:
            if task.end_date < date.today():
                result[0].add(task)
            if task.end_date == date.today():
                result[1].add(task)
            if task.end_date > date.today() and task.end_date < (date.today() + timedelta(days=6)):
                result[2].add(task)
    return result
