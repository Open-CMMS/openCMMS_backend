from django.contrib.auth.models import Permission
from django.test import TestCase
from rest_framework.test import APIClient
from usersmanagement.models import Team, TeamType, UserProfile
from usersmanagement.serializers import (
    TeamTypeDetailsSerializer,
    TeamTypeSerializer,
)


class TeamTypeTests(TestCase):

    def setUp(self):
        """
            Set-up team, team type for the tests
        """
        admin_type = TeamType.objects.create(name="Administrators")
        admin_team = Team.objects.create(name="Administrators")
        admin_team.set_team_type(admin_type)

    def add_view_perm(self, user):
        """
            Add view permission to user
        """
        perm_view = Permission.objects.get(codename="view_teamtype")
        user.user_permissions.set([perm_view])

    def add_add_perm(self, user):
        """
            Add add permission to user
        """
        perm_add = Permission.objects.get(codename="add_teamtype")
        user.user_permissions.set([perm_add])

    def add_change_perm(self, user):
        """
            Add change permission to user
        """
        perm_change = Permission.objects.get(codename="change_teamtype")
        user.user_permissions.set([perm_change])

    def add_delete_perm(self, user):
        """
            Add delete permission to user
        """
        perm_delete = Permission.objects.get(codename="delete_teamtype")
        user.user_permissions.set([perm_delete])

    def test_US1_I1_teamtypeslist_get_with_perm(self):
        """
            Test if a user with perm receive the teamtypes' list.

            Inputs:
                user (UserProfile): a user with permissions to view team types.
                serializer (TeamTypeSerializer): a serializer containing all team types data.

            Expected Output:
                We expect a 200 status code in the response.
                We expect to get in the response the same data as in serializer.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        teamtypes = TeamType.objects.all()
        serializer = TeamTypeSerializer(teamtypes, many=True)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/usersmanagement/teamtypes/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_US1_I1_teamtypeslist_get_without_perm(self):
        """
            Test if a user without perm can't receive the teamtypes' list.

            Inputs:
                user (UserProfile): a user without permissions to view team types.

            Expected Output:
                We expect a 401 status code in the response.
        """
        user = UserProfile.objects.create(username="user")
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/usersmanagement/teamtypes/")
        self.assertEqual(response.status_code, 401)

    def test_US1_I2_teamtypeslist_post_with_perm(self):
        """
            Test if a user with perm can add a teamtype.

            Inputs:
                user (UserProfile): a user with permissions to add team types.
                post data (JSON): a mock-up for a team type.

            Expected Output:
                We expect a 201 status code in the response.
                We expect to find the created team type.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)

        response = c.post(
            "/api/usersmanagement/teamtypes/", {
                "name": "test_teamtype",
                "perms": [3],
                "team_set": [Team.objects.get(name="Administrators").id]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(TeamType.objects.get(name="test_teamtype"))

    def test_US1_I2_teamtypeslist_post_without_perm(self):
        """
            Test if a user without perm can't add a teamtype.

            Inputs:
                user (UserProfile): a user without permissions to add team types.
                post data (JSON): a mock-up for a team type.

            Expected Output:
                We expect a 401 status code in the response.
        """
        user = UserProfile.objects.create(username="user")
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.post(
            "/api/usersmanagement/teamtypes/", {
                "name": "test_teamtype",
                "perms": [3],
                "team_set": [Team.objects.get(name="Administrators").id]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_US1_I3_teamtypesdetail_get_with_perm(self):
        """
            Test if a user with perm can get a teamtype.

            Inputs:
                user (UserProfile): a user with permissions to view team types.
                serializer (TeamTypeDetailsSerializer): a serializer containing a team type data.

            Expected Output:
                We expect a 200 status code in the response.
                We expect to get in the response the same data as in serializer.
        """
        user = UserProfile.objects.create(username="user")
        self.add_view_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)

        team_type = TeamType.objects.get(name="Administrators")
        serializer = TeamTypeDetailsSerializer(team_type)
        response = c.get("/api/usersmanagement/teamtypes/" + str(team_type.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_US1_I3_teamtypesdetail_get_without_perm(self):
        """
            Test if a user without perm can't get a teamtype.

            Inputs:
                user (UserProfile): a user without permissions to view team types.

            Expected Output:
                We expect a 401 status code in the response.
        """
        user = UserProfile.objects.create(username="user")
        c = APIClient()
        c.force_authenticate(user=user)
        team_type = TeamType.objects.get(name="Administrators")
        response = c.get("/api/usersmanagement/teamtypes/" + str(team_type.id) + "/")
        self.assertEqual(response.status_code, 401)

    def test_US1_I4_teamtypesdetail_put_with_perm(self):
        """
            Test if a user with perm can change a teamtype.

            Inputs:
                user (UserProfile): a user with permissions to change team types.
                put data (JSON): a mock-up for an updated team type.

            Expected Output:
                We expect a 200 status code in the response.
                We expect to find the updated team type.
        """
        user = UserProfile.objects.create(username="user")
        self.add_change_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        team_type = TeamType.objects.get(name="Administrators")

        response = c.put(
            "/api/usersmanagement/teamtypes/" + str(team_type.id) + "/", {
                "name": "test_teamtype",
                "perms": [3],
                "team_set": [Team.objects.get(name="Administrators").id]
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(TeamType.objects.get(name="test_teamtype"))

    def test_US1_I4_teamtypesdetail_put_without_perm(self):
        """
            Test if a user without perm can't change a teamtype.

            Inputs:
                user (UserProfile): a user without permissions to change team types.
                put data (JSON): a mock-up for an updated team type.

            Expected Output:
                We expect a 401 status code in the response.
        """
        user = UserProfile.objects.create(username="user")
        c = APIClient()
        c.force_authenticate(user=user)
        team_type = TeamType.objects.get(name="Administrators")

        response = c.put(
            "/api/usersmanagement/teamtypes/" + str(team_type.id) + "/", {
                "name": "test_teamtype",
                "perms": [3],
                "team_set": [Team.objects.get(name="Administrators").id]
            },
            format='json'
        )

        self.assertEqual(response.status_code, 401)

    def test_US1_I5_teamtypesdetail_delete_with_perm(self):
        """
            Test if a user with perm can delete a teamtype.

            Inputs:
                user (UserProfile): a user with permissions to delete team types.

            Expected Output:
                We expect a 204 status code in the response.
                We expect to not find the deleled team type.
        """
        user = UserProfile.objects.create(username="user")
        self.add_delete_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        team_type = TeamType.objects.get(name="Administrators")
        response = c.delete("/api/usersmanagement/teamtypes/" + str(team_type.id) + "/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(TeamType.objects.filter(id=team_type.id).exists())

    def test_US1_I5_teamtypesdetail_delete_without_perm(self):
        """
            Test if a user without perm can't delete a teamtype.

            Inputs:
                user (UserProfile): a user without permissions to delete team types.

            Expected Output:
                We expect a 401 status code in the response.
        """
        user = UserProfile.objects.create(username="user")
        c = APIClient()
        c.force_authenticate(user=user)
        team_type = TeamType.objects.get(name="Administrators")
        response = c.delete("/api/usersmanagement/teamtypes/" + str(team_type.id) + "/")
        self.assertEqual(response.status_code, 401)
