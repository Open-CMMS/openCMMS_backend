"""This files allows to send notifications."""

from datetime import date, timedelta

from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from maintenancemanagement.models import Task
from usersmanagement.models import UserProfile


def send_notifications():
    for user in UserProfile.objects.all():
        template = get_notification_template(user)
        if template:
            plain_message = strip_tags(template)
            mail.send_mail(
                'Notification Open-CMMS', plain_message, settings.EMAIL_HOST_USER, [user.email], html_message=template
            )


def get_notification_template(user):
    tasks = get_imminent_tasks(user)
    if len(tasks[0]) + len(task[1]) + len(task[2]) > 0:
        return render_to_string('nom_de_template_html', {'tasks': tasks})
    return None


def get_imminent_tasks(user):
    result = (set(), set(), set())
    tasks = Task.objects.filter(teams__pk__in=user.groups.all().values_list("id", flat=True).iterator())
    for task in tasks:
        if task.end_date:
            if task.end_date < date.today():
                result[0].add(task)
            if task.end_date == date.today():
                result[1].add(task)
            if task.end_date > date.today() and task.end_date < (date.today() + timedelta(days=6)):
                result[2].add(task)
    return result


# UserProfile -> Team -> Tasker.
# Task renvoyées sous cette forme : (set en retard, set journée, set semaine)
