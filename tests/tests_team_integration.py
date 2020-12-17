from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase
from openCMMS import settings
from rest_framework.test import APIClient
from usersmanagement.models import Team, TeamType, UserProfile
from usersmanagement.serializers import (
    PermissionSerializer,
    TeamDetailsSerializer,
    TeamSerializer,
    UserProfileSerializer,
)
from usersmanagement.views.views_team import belongs_to_team

User = settings.AUTH_USER_MODEL


class TeamsTests(TestCase):

    def set_up(self):
        """
            Set up team types, teams, users, permissions for the tests
        """
        #Creation of 3 TeamTypes
        Admins = TeamType.objects.create(name="Administrators")
        MMs = TeamType.objects.create(name="Maintenance Manager")
        MTs = TeamType.objects.create(name="Maintenance Team")

        #Create and add permissions du admin
        content_type = ContentType.objects.get_for_model(Team)
        permission = Permission.objects.get(codename='add_team')
        permission2 = Permission.objects.get(codename='view_team')
        permission3 = Permission.objects.get(codename='delete_team')
        permission4 = Permission.objects.get(codename='change_team')

        #Creation of the 3 inital Teams
        T_Admin = Team.objects.create(name="Administrators 1", team_type=Admins)
        T_MM1 = Team.objects.create(name="Maintenance Manager 1", team_type=MMs)
        T_MT1 = Team.objects.create(name="Maintenance Team 1", team_type=MTs)

        #User creation
        tom = UserProfile.objects.create(
            first_name="Tom", last_name="N", email="tom.n@ac.com", password="truc", username="tn"
        )

        joe = UserProfile.objects.create(
            first_name="Joe", last_name="D", email="joe.d@ll.com", password="bouh", username="jd"
        )

        joey = UserProfile.objects.create(
            first_name="Joey",
            last_name="Bidouille",
            email="joey.bidouille@machin.com",
            password="brico",
            username="jbi"
        )

        tom.groups.add(T_Admin)
        tom.save()
        tom.user_permissions.add(permission)
        tom.user_permissions.add(permission2)
        tom.user_permissions.add(permission3)
        tom.user_permissions.add(permission4)
        tom.save()

        joe.groups.add(T_MT1)
        joe.save()

    def test_US3_I1_addusertoteam_post_with_perm(self):
        """
            Test if a user with permission can add a user to a team.

            Inputs:
                user (UserProfile): a user to add to a team.
                team (Team): a team in which to add a user.

            Expected Output:
                We expect a 201 status code in the response.
                We expect to find user in the team.
        """
        self.set_up()
        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_authenticate(user=tom)

        user = UserProfile.objects.get(username="jd")
        team = Team.objects.get(name="Administrators 1")

        response = c.post(
            "/api/usersmanagement/add_user_to_team", {
                'id_user': user.pk,
                'id_team': team.pk
            }, format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(user.groups.get(name="Administrators 1").name, team.name)

    def test_US3_I1_addusertoteam_post_without_perm(self):
        """
            Test if a user without permission can't add a user to a team.

            Inputs:
                user (UserProfile): a user to add to a team.
                team (Team): a team in which to add a user.

            Expected Output:
                We expect a 401 status code in the response.
        """
        self.set_up()
        c = APIClient()

        joey = UserProfile.objects.get(username="jbi")
        c.force_authenticate(user=joey)

        response = c.post(
            "/api/usersmanagement/add_user_to_team", {
                'username': 'jbi',
                'team_name': 'Administrators 1'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 401)

    def test_US3_I1_addusertoteam_put_with_perm(self):
        """
            Test if a user with permission can remove a user to a team.

            Inputs:
                user (UserProfile): a user to add to a team.
                team (Team): a team in which to add a user.

            Expected Output:
                We expect a 201 status code in the response.
                We expect to find user in the team.
        """
        self.set_up()
        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_authenticate(user=tom)

        user = UserProfile.objects.get(username="jd")
        team = Team.objects.get(name="Administrators 1")

        response = c.put(
            "/api/usersmanagement/add_user_to_team", {
                'id_user': user.pk,
                'id_team': team.pk
            }, format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertFalse(user.groups.filter(name="Administrators 1").exists())

    def test_US3_I1_addusertoteam_put_without_perm(self):
        """
            Test if a user without permission can't remove a user to a team.

            Inputs:
                user (UserProfile): a user to add to a team.
                team (Team): a team in which to add a user.

            Expected Output:
                We expect a 401 status code in the response.
        """
        self.set_up()
        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_authenticate(user=joe)

        response = c.put(
            "/api/usersmanagement/add_user_to_team", {
                'username': 'jbi',
                'team_name': 'Administrators 1'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 401)

    def test_US3_I2_teamlist_get_with_perm(self):
        """
            Test if a user with permission can view the teams' list.

            Inputs:
                serializer (TeamSerializer): a serializer containing all teams data.

            Expected Output:
                We expect a 200 status code in the response.
                We expect to get in the response the same data as in serializer.
        """
        self.set_up()

        teams = Team.objects.all()
        serializer = TeamSerializer(teams, many=True)

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_authenticate(user=tom)

        response = c.get("/api/usersmanagement/teams/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_US3_I2_teamlist_get_without_perm(self):
        """
            Test if a user without permission can't view the teams' list.

            Inputs:

            Expected Output:
                We expect a 401 status code in the response.
        """
        self.set_up()

        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_authenticate(user=joe)

        response = c.get("/api/usersmanagement/teams/")

        self.assertEqual(response.status_code, 401)

    def test_US3_I3_teamlist_post_with_perm(self):
        """
            Test if a user with permission can add a team.

            Inputs:
                post data (Team): a mock-up for a team.

            Expected Output:
                We expect a 200 status code in the response.
                We expect to find the created team.
                We expect that the created team as the good team type.
        """
        self.set_up()

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_authenticate(user=tom)

        tt = TeamType.objects.all()[0]

        response = c.post(
            "/api/usersmanagement/teams/", {
                "name": "test_team",
                "team_type": str(tt.id),
                'user_set': []
            },
            format='json'
        )
        team = Team.objects.get(pk=response.data.get("data")['id'])
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Team.objects.filter(name="test_team"))
        self.assertEqual(team.team_type, tt)

    def test_US3_I3_teamlist_get_without_perm(self):
        """
            Test if a user without permission can't add a team.

            Inputs:
                post data (Team): a mock-up for a team.

            Expected Output:
                We expect an error in the response.
        """
        self.set_up()

        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_authenticate(user=joe)

        response = c.post("/api/usersmanagement/teams/", {"name": "test_team"}, format='json')
        self.assertEqual(response.data["error"], "You don't have this permission")

    def test_US3_I4_teamdetail_get_with_perm(self):
        """
            Test if a user with permission can view a team.

            Inputs:
                serializer (TeamDetailsSerializer): a serializer containing a team data.

            Expected Output:
                We expect a 200 status code in the response.
                We expect to get in the response the same data as in serializer.
        """
        self.set_up()

        team = Team.objects.get(name="Administrators 1")
        serializer = TeamDetailsSerializer(team)

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_authenticate(user=tom)

        address = "/api/usersmanagement/teams/" + str(team.id)

        response = c.get(address)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_US3_I4_teamdetail_get_without_perm(self):
        """
            Test if a user without permission can't view a team.

            Inputs:

            Expected Output:
                We expect a 401 status code in the response.
        """
        self.set_up()

        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_authenticate(user=joe)

        team = Team.objects.get(name="Administrators 1")

        address = "/api/usersmanagement/teams/" + str(team.id)

        response = c.get(address)

        self.assertEqual(response.status_code, 401)

    def test_US3_I5_teamdetail_put_with_perm(self):
        """
            Test if a user with permission can change a team's name.

            Inputs:
                put data (JSON): a mock-up of an updated team.

            Expected Output:
                We expect a 200 status code in the response.
                We expect to find updated team.
        """
        self.set_up()

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_authenticate(user=tom)

        team = Team.objects.get(name="Administrators 1")
        address = "/api/usersmanagement/teams/" + str(team.id)

        response = c.put(address, {"name": "new_name"}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], "new_name")

    def test_US3_I5_teamdetail_put_with_perm(self):
        """
            Test if a user with permission can change a team's team type.

            Inputs:
                put data (JSON): a mock-up of an updated team.

            Expected Output:
                We expect a 200 status code in the response.
                We expect to find updated team.
        """
        self.set_up()

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_authenticate(user=tom)

        team = Team.objects.get(name="Administrators 1")
        address = "/api/usersmanagement/teams/" + str(team.id)

        tt = TeamType.objects.all()[1]

        response = c.put(address, {"team_type": str(tt.id)}, format='json')

        teamApres = Team.objects.get(pk=response.data['id'])
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(team.team_type, teamApres.team_type)

    def test_US3_I5_teamdetail_put_without_perm(self):
        """
            Test if a user without permission can't change a team's informations

            Inputs:
                put data (JSON): a mock-up of an updated team.

            Expected Output:
                We expect a 401 status code in the response.
        """
        self.set_up()

        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_authenticate(user=joe)

        team = Team.objects.get(name="Administrators 1")

        address = "/api/usersmanagement/teams/" + str(team.id)

        response = c.put(address, {"name": "new_name"}, format="json")

        self.assertEqual(response.status_code, 401)

    def test_US3_I6_teamdetail_delete_with_perm(self):
        """
            Test if a user with permission can delete a team.

            Inputs:
                delete data (JSON): the id of the team to be deleted.

            Expected Output:
                We expect a 204 status code in the response.
                We expect to not find deleted team.
        """
        self.set_up()

        c = APIClient()
        team = Team.objects.get(name="Maintenance Team 1")

        tom = UserProfile.objects.get(username="tn")
        c.force_authenticate(user=tom)

        address = "/api/usersmanagement/teams/" + str(team.id)

        response = c.delete(address)

        self.assertEqual(response.status_code, 204)
        with self.assertRaises(Team.DoesNotExist):
            team_final = Team.objects.get(name="Maintenance Team 1")

    def test_US3_I6_teamdetail_delete_without_perm(self):
        """
            Test if a user without permission can't delete a team.

            Inputs:
                delete data (JSON): the id of the team to be deleted.

            Expected Output:
                We expect a 401 status code in the response.
        """
        self.set_up()

        c = APIClient()
        team = Team.objects.get(name="Maintenance Team 1")

        joe = UserProfile.objects.get(username="jd")
        c.force_authenticate(user=joe)

        address = "/api/usersmanagement/teams/" + str(team.id)

        response = c.delete(address)

        self.assertEqual(response.status_code, 401)
