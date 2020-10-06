import datetime

from django.test import TestCase
from usersmanagement.models import Team, TeamType, UserProfile
from utils.notifications import *


class NotificationsTests(TestCase):
    """
        Tests for notifications system.
    """

    def set_up(self):
        """
            Set up team types, teams, users, permissions for the tests
        """
        #Creation of 3 TeamTypes
        T_MT1 = Team.objects.create(name="Maintenance Team 1", team_type=MTs)

        #User creation

        joe = UserProfile.objects.create(
            first_name="Joe", last_name="D", email="joe.d@ll.com", password="bouh", username="jd"
        )

        joe.groups.add(T_MT1)
        joe.save()
        team = Team.objects.create(name="team")
        task1 = Task.objects.create(name="task_today", end_date=datetime.date.today())
        task2 = Task.objects.create(name="task_yesterday", end_date=datetime.date.today() - datetime.timedelta(days=1))
        task3 = Task.objects.create(name="task_tomorrow", end_date=datetime.date.today() + datetime.timedelta(days=1))
        task1.teams.add(team)
        task1.save()
        task2.teams.add(team)
        task2.save()
        task3.teams.add(team)
        task3.save()
        team.user_set.add(joe)
        team.save()

    def test_get_imminent_tasks(self):
        self.set_up()
        tasks = get_imminent_tasks(UserProfile.objects.get(username="jd"))
        self.assertTrue(Task.objects.get(name="task_yesterday") in tasks[0])
        self.assertTrue(Task.objects.get(name="task_today") in tasks[1])
        self.assertTrue(Task.objects.get(name="task_tomorrow") in tasks[2])
