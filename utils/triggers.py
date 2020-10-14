"""This modules implements automatic triggering of tasks."""

from datetime import date

from django.db.models import Q
from maintenancemanagement.models import Field, FieldGroup, FieldObject, Task

# A FAIRE : FLOAT
# Déclenchement manuel : date et float : on vérifie avec Scheduler (date
# quotidiennement, float toutes les 5 minutes) si une est vraie on
# valide et on passe le statut à false

# Pour les déclenchements:
# Pour la date : on compare avec un today
# Pour le float : pour l'instant on moque pour les tests


def activate_triggered_tasks():
    """Activate waiting tasks if a trigger condition is true."""
    tasks = Task.objects.filter(over=None)
    for task in tasks:
        if task_is_triggered(task):
            task.over = False
            task.save()


def task_is_triggered(task):
    """Check if a trigger condition is true for the given task."""
    date_conditons = FieldObject.objects.filter(
        Q(field=Field.objects.get(Q(field_group=FieldGroup.objects.get(name='Trigger Conditions')) & Q(name='Date'))) &
        Q(object_id=task.id)
    )
    for date_condition in date_conditons:
        if date.fromisoformat(date_condition.value) <= date.today():
            return True
    return False
