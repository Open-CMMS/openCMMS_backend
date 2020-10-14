"""This modules implements automatic triggering of tasks."""

from datetime import date

from django.contrib.contenttypes import fields
from django.db.models import Q
from maintenancemanagement.models import Field, FieldGroup, FieldObject, Task

# Il faut qu'on récupère :
# On récupère les taches à null
# on vérifie les condition. Si l'une passe à True, l'état de la tache passe à false.
# # À faire à l'envers

# Récupération des taches à Null
# Déclenchement manuel : date et float : on vérifie avec Scheduler (date quotidiennement, float toutes les 5 minutes) si une est vraie on valide et on passe le statut à false

# Pour les déclenchements:
# Pour la date : on compare avec un today
# Pour le float : pour l'instant on moque pour les tests


def activate_triggered_tasks():
    tasks = Task.objects.filter(over=None)
    for task in tasks:
        if task_is_triggered(task):
            task.over = False
            task.save()


def task_is_triggered(task):
    date_conditons = FieldObject.objects.filter(
        Q(field=Field.objects.get(Q(field_group=FieldGroup.objects.get(name='Trigger Conditions')) & Q(name='Date'))) &
        Q(object_id=task.id)
    )
    for date_condition in date_conditons:
        if date.fromisoformat(date_condition.value) <= date.today():
            return True
    return False
