from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase
from maintenancemanagement.models import Task
from maintenancemanagement.views.views_task import participate_to_task
from rest_framework.test import APIClient
from usersmanagement.models import Team, TeamType, UserProfile


class TeamsTests(TestCase):

    def set_up(self):
        """
            Set up team types, teams, users, permissions for the tests
        """
        MTs = TeamType.objects.create(name="Maintenance Team")

        T_MT1 = Team.objects.create(name="Maintenance Team 1", team_type=MTs)
        T_MT2 = Team.objects.create(name="Maintenance Team 2", team_type=MTs)

        #User creation
        tom = UserProfile.objects.create(
            first_name="Tom", last_name="N", email="tom.n@ac.com", password="truc", username="tn"
        )

        joe = UserProfile.objects.create(
            first_name="Joe", last_name="D", email="joe.d@ll.com", password="bouh", username="jd"
        )

        tom.groups.add(T_MT1)
        tom.save()

        joe.groups.add(T_MT2)
        joe.save()

        task = Task.objects.create(name="something", description="things to do")
        task.teams.add(T_MT1)
        task.save()

    def test_US5_U1_participate_to_task_true(self):
        """
            Test if a user participating to a task send true
        """
        self.set_up()

        tom = UserProfile.objects.get(username="tn")

        task = Task.objects.get(name="something")

        self.assertTrue(participate_to_task(tom, task))

    def test_US5_U1_participate_to_task_false(self):
        """
            Test if a user not participating to a task send false
        """
        self.set_up()

        joe = UserProfile.objects.get(username="jd")

        task = Task.objects.get(name="something")

        self.assertFalse(participate_to_task(joe, task))
