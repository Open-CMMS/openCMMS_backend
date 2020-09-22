from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase
from rest_framework.test import APIClient
from usersmanagement.models import Team, TeamType, UserProfile
from usersmanagement.serializers import (
    PermissionSerializer, TeamSerializer, UserProfileSerializer,
)
from usersmanagement.views.views_team import belongs_to_team


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

    def test_belongs_to_team_true(self):
        """
            Test if a user belonging to a team send true
        """
        self.set_up()

        joe = UserProfile.objects.get(username="jd")

        team = Team.objects.get(name="Maintenance Team 1")

        self.assertTrue(belongs_to_team(joe, team))

    def test_belongs_to_team_false(self):
        """
            Test if a user not belonging to a team send false
        """
        self.set_up()

        joe = UserProfile.objects.get(username="jd")

        team = Team.objects.get(name="Administrators 1")

        self.assertFalse(belongs_to_team(joe, team))
