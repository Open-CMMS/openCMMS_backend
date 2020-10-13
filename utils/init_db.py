"""This script initiate the database with some default values"""
from django.contrib.contenttypes.models import ContentType
from maintenancemanagement.models import (
    EquipmentType,
    Field,
    FieldGroup,
    FieldValue,
    Task,
)
from usersmanagement.models import Permission, Team, TeamType, UserProfile


def main():
    FieldGroup.objects.create(name="End Conditions", is_equipment=False)
    FieldGroup.objects.create(name="Trigger Conditions", is_equipment=False)

    # Creation of 3 TeamTypes
    admins = TeamType.objects.create(name="Administrators")
    maintenance_managers = TeamType.objects.create(name="Maintenance Manager")
    maintenance_teams = TeamType.objects.create(name="Maintenance Team")

    # Creation of the 3 inital Teams
    Team.objects.create(name="Administrators 1", team_type=admins)
    Team.objects.create(name="Maintenance Manager 1", team_type=maintenance_managers)
    Team.objects.create(name="Maintenance Team 1", team_type=maintenance_teams)

    content_type = ContentType.objects.get_for_model(Task)
    Permission.objects.create(codename='add_tasktemplate', name='Can add task template', content_type=content_type)
    Permission.objects.create(codename='view_tasktemplate', name='Can view task template', content_type=content_type)
    Permission.objects.create(
        codename='delete_tasktemplate', name='Can change task template', content_type=content_type
    )

    # Adding all permissions to admins
    permissions_admin = Permission.objects.all()
    for permission in permissions_admin:
        admins.perms.add(permission)

    # Adding permissions to maintenance managers

    liste_manager_management = [
        'equipment', 'equipmenttype', 'field', 'fieldgroup', 'fieldvalue', 'file', 'task', 'tasktemplate'
    ]
    permissions_tasktemplate = Permission.objects.filter(codename__regex='|'.join(liste_manager_management)
                                                        ).exclude(codename__endswith='profile')

    liste_manager_user = ['Can change team', 'Can view user profile', 'Can view team', 'Can add team']
    permissions_managers_users = Permission.objects.filter(name__in=liste_manager_user)
    for permission in permissions_tasktemplate:
        maintenance_managers.perms.add(permission)

    for permission in permissions_managers_users:
        maintenance_managers.perms.add(permission)

    # Adding permissions to maintenance teams
    liste_team = [
        'Can view file',
        'Can view equipment',
        'Can view field',
        'Can view field group',
        'Can view field value',
        'Can change field value',
        'Can view task',
    ]

    permissions_maintenance_team = Permission.objects.filter(name__in=liste_team)

    for permission in permissions_maintenance_team:
        maintenance_teams.perms.add(permission)
    # permissions_team
