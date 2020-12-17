from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from usersmanagement.models import Team, TeamType


class TeamTypeTests(TestCase):

    def setUp(self):
        """
            Set up permissions, team, team type for the tests.
        """
        perm_1 = Permission.objects.get(id=1)
        perm_2 = Permission.objects.get(id=2)
        admin_type = TeamType.objects.create(name="Administrators")
        admin_team = Team.objects.create(name="Administrators")
        admin_team.set_team_type(admin_type)
        admin_type.perms.add(perm_1, perm_2)

    def test_US1_U1_create_get_team_type(self):
        """
            Test the creation of a team type in the model.

            Inputs:
                MaintenanceManager_type (TeamType): a team type to create.

            Expected Output:
                We expect to find the created team type.
        """
        MaintenanceManager_type = TeamType.objects.create(name="Maintenance Manager")
        self.assertEqual(MaintenanceManager_type, TeamType.objects.get(name="Maintenance Manager"))

    def test_US1_U2_add_perm(self):
        """
            Test the addition of a permission on a team type.

            Inputs:
                MaintenanceManager_type (TeamType): a team type to add a perm.
                perm (Permission): a perm to add to the team type.

            Expected Output:
                We expect to find that the team type has the perm.
        """
        perm = Permission.objects.get(id=1)
        MaintenanceManager_type = TeamType.objects.create(name="Maintenance Manager")
        MaintenanceManager_type.perms.add(perm)
        self.assertEqual(MaintenanceManager_type.perms.get(id=1), perm)

    def test_US1_U3_apply_(self):
        """
            Test add a set of permissions to a set of teams.

            Inputs:
                admin_type (TeamType): a team type with perms.
                admin_team (Team): a team of team type admin_type.

            Expected Output:
                We expect to find that admin_team has perms of admin_type.
        """
        admin_type = TeamType.objects.get(name="Administrators")
        admin_type._apply_()
        admin_team = Team.objects.get(name="Administrators")
        self.assertEqual(admin_team.permissions.get(id=1), Permission.objects.get(id=1))
        self.assertEqual(admin_team.permissions.get(id=2), Permission.objects.get(id=2))

    def test_US1_U4_apply_change_teamtype(self):
        """
            Test change teamtype.

            Inputs:
                admin_type (TeamType): a team type with perms.
                admin_team (Team): a team of team type admin_type.

            Expected Output:
                We expect to find that admin_team the added perm of admin_type.
        """
        perm_3 = Permission.objects.get(id=3)
        MaintenanceManager_type = TeamType.objects.create(name="Maintenance Manager")
        MaintenanceManager_type.perms.add(perm_3)
        admin_team = Team.objects.get(name="Administrators")
        admin_team.set_team_type(MaintenanceManager_type)
        self.assertEqual(admin_team.permissions.get(id=3), perm_3)
