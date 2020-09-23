from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from usersmanagement.models import Team, TeamType


class TeamTypeTests(TestCase):

    def setUp(self):
        """
            Set up permissions, team, team type for the tests
        """
        perm_1 = Permission.objects.get(id=1)
        perm_2 = Permission.objects.get(id=2)
        admin_type = TeamType.objects.create(name="Administrators")
        admin_team = Team.objects.create(name="Administrators")
        admin_team.set_team_type(admin_type)
        admin_type.perms.add(perm_1, perm_2)

    def test_create_get_team_type(self):
        """
            Test the creation of a team type in the model
        """
        MaintenanceManager_type = TeamType.objects.create(name="Maintenance Manager")
        self.assertEqual(MaintenanceManager_type, TeamType.objects.get(name="Maintenance Manager"))

    def test_add_perm(self):
        """
            Test the addition of a permission on a team type
        """
        perm = Permission.objects.get(id=1)
        MaintenanceManager_type = TeamType.objects.create(name="Maintenance Manager")
        MaintenanceManager_type.perms.add(perm)
        self.assertEqual(MaintenanceManager_type.perms.get(id=1), perm)

    def test_apply_(self):
        """
            Test add a set of permissions to a set of teams
        """
        admin_type = TeamType.objects.get(name="Administrators")
        admin_type._apply_()
        admin_team = Team.objects.get(name="Administrators")
        self.assertEqual(admin_team.permissions.get(id=1), Permission.objects.get(id=1))
        self.assertEqual(admin_team.permissions.get(id=2), Permission.objects.get(id=2))

    def test_apply_change_teamtype(self):
        """
            Test change teamtype
        """
        perm_3 = Permission.objects.get(id=3)
        MaintenanceManager_type = TeamType.objects.create(name="Maintenance Manager")
        MaintenanceManager_type.perms.add(perm_3)
        admin_team = Team.objects.get(name="Administrators")
        admin_team.set_team_type(MaintenanceManager_type)
        self.assertEqual(admin_team.permissions.get(id=3), perm_3)
