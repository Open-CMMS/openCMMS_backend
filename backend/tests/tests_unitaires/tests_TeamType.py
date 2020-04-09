from django.contrib.auth.models import Permission
from django.test import TestCase
from usersmanagement.models import TeamType,Team

class TeamTypeTests(TestCase):

    def setUp(self):
        perm_1 = Permission.objects.get(id=1)
        perm_2 = Permission.objects.get(id=2)
        admin_type = TeamType.objects.create(name="Administrators")
        admin_type.perms.add(perm_1, perm_2)

    def test_get_team_type(self):
        MaintenanceManager_type = TeamType.objects.create(name="Maintenance Manager")
        self.assertEqual(MaintenanceManager_type, TeamType.objects.get(name="Maintenance Manager"))

    def test_set_perm(self):
        perm = Permission.objects.get(id=1)
        MaintenanceManager_type = TeamType.objects.create(name="Maintenance Manager")
        MaintenanceManager_type.perms.add(perm)
        self.assertEqual(MaintenanceManager_type.perms.get(id=1),perm)

    def test_apply_(self):
        admin_type = TeamType.objects.get(name="Administrators")
        admin_team = Team.objects.create(name="Administrators",
                                        team_type=admin_type)
        admin_type.apply()

        self.assertEqual(admin_team.permissions.get(id=1),Permission.objects.get(id=1))
        self.assertEqual(admin_team.permissions.get(id=2), Permission.objects.get(id=2))
