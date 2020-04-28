from django.contrib.auth.models import Permission
from django.test import TestCase, Client
from usersmanagement.models import TeamType,Team

class TeamTypeTests(TestCase):

    def setUp(self):
        perm_1 = Permission.objects.get(id=1)
        perm_2 = Permission.objects.get(id=2)
        admin_type = TeamType.objects.create(name="Administrators")
        admin_team = Team.objects.create(name="Administrators")
        admin_team.set_team_type(admin_type)
        admin_type.perms.add(perm_1, perm_2)

    def test_create_get_team_type(self):
        MaintenanceManager_type = TeamType.objects.create(name="Maintenance Manager")
        self.assertEqual(MaintenanceManager_type, TeamType.objects.get(name="Maintenance Manager"))

    def test_add_perm(self):
        perm = Permission.objects.get(id=1)
        MaintenanceManager_type = TeamType.objects.create(name="Maintenance Manager")
        MaintenanceManager_type.perms.add(perm)
        self.assertEqual(MaintenanceManager_type.perms.get(id=1),perm)

    def test_apply_(self):
        admin_type = TeamType.objects.get(name="Administrators")
        admin_type._apply_()
        admin_team = Team.objects.get(name="Administrators")
        self.assertEqual(admin_team.permissions.get(id=1),Permission.objects.get(id=1))
        self.assertEqual(admin_team.permissions.get(id=2), Permission.objects.get(id=2))

    def test_apply_change_teamtype(self):
        perm_3 = Permission.objects.get(id=3)
        MaintenanceManager_type = TeamType.objects.create(name="Maintenance Manager")
        MaintenanceManager_type.perms.add(perm_3)
        admin_team = Team.objects.get(name="Administrators")
        admin_team.set_team_type(MaintenanceManager_type)
        self.assertEqual(admin_team.permissions.get(id=3), perm_3)

