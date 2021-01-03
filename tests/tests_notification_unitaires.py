import datetime

from usersmanagement.models import Team, TeamType, UserProfile
from utils.notifications import *

from django.contrib.auth.models import User
from django.test import TestCase


class NotificationsTests(TestCase):
    """
        Tests for notifications system.
    """

    def set_up(self):
        """
            Set up team types, teams, users, permissions for the tests
        """
        mts = TeamType.objects.create(name="Maintenance Team")

        #Creation of 3 TeamTypes
        t_mt1 = Team.objects.create(name="Maintenance Team 1", team_type=mts)

        #User creation

        joe = UserProfile.objects.create(
            first_name="Joe", last_name="D", email="joe.d@ll.com", password="bouh", username="jd"
        )

        joe.groups.add(t_mt1)
        joe.save()
        UserProfile.objects.create(username='toto')
        team = Team.objects.create(name="team")
        task1 = Task.objects.create(name="task_today", end_date=datetime.date.today())
        task2 = Task.objects.create(name="task_yesterday", end_date=datetime.date.today() - datetime.timedelta(days=1))
        task3 = Task.objects.create(name="task_tomorrow", end_date=datetime.date.today() + datetime.timedelta(days=1))
        achieved_task = Task.objects.create(name="achieved_task", end_date=datetime.date.today(), over=True)
        task1.teams.add(team)
        task1.save()
        task2.teams.add(team)
        task2.save()
        task3.teams.add(team)
        task3.save()
        achieved_task.teams.add(team)
        achieved_task.save()
        team.user_set.add(joe)
        team.save()

    def test_US17_U1_get_imminent_tasks_user_with_tasks(self):
        """
        Test if we can retrieve the tasks an user with tasks has to do

                Inputs:
                    user (UserProfile): A UserProfile we create with tasks to do

                Expected outputs:
                    We expect all the tasks the user has to do well separed in different sublists
        """
        self.set_up()
        tasks = get_imminent_tasks(UserProfile.objects.get(username='jd'))
        self.assertTrue(Task.objects.get(name='task_yesterday') in tasks[0])
        self.assertTrue(Task.objects.get(name='task_today') in tasks[1])
        self.assertTrue(Task.objects.get(name='task_tomorrow') in tasks[2])

    def test_US17_U1_get_imminent_tasks_user_without_tasks(self):
        """
        Test if we retrieve no tasks from an user without tasks to do

                Inputs:
                    user (UserProfile): A UserProfile we create without tasks to do

                Expected outputs:
                    We expect to retrieve no tasks in all the sublists
        """
        self.set_up()
        tasks = get_imminent_tasks(UserProfile.objects.get(username='toto'))
        self.assertFalse(tasks[0])
        self.assertFalse(tasks[1])
        self.assertFalse(tasks[2])

    def test_US17_U2_get_notification_template_user_with_tasks(self):
        """
        Test if we retrieve a template when an user has tasks to do

                Inputs:
                    user (UserProfile): A UserProfile we create with tasks to do

                Expected outputs:
                    We expect to retrieve the template
        """
        self.set_up()
        user = UserProfile.objects.get(username='jd')
        template = get_notification_template(user)
        self.assertTrue(template)

    def test_US17_U2_get_notification_template_user_without_tasks(self):
        """
        Test if we retrieve a template when an user hasn't tasks to do

                Inputs:
                    user (UserProfile): A UserProfile we create without tasks to do

                Expected outputs:
                    We expect to not retrieve the template
        """
        self.set_up()
        user = UserProfile.objects.get(username='toto')
        template = get_notification_template(user)
        self.assertFalse(template)

    def test_US17_U3_get_imminent_tasks_user_with_some_achieved_tasks(self):
        """
        Test if we retrieve achieved tasks when an user has already completed tasks he had to do

                Inputs:
                    user (UserProfile): A UserProfile we create with tasks to do and achieved tasks

                Expected outputs:
                    We expect to not retrieve achieved task in all the sublists
        """
        self.set_up()
        tasks = get_imminent_tasks(UserProfile.objects.get(username='jd'))
        self.assertFalse(Task.objects.get(name='achieved_task') in tasks[0])
        self.assertFalse(Task.objects.get(name='achieved_task') in tasks[1])
        self.assertFalse(Task.objects.get(name='achieved_task') in tasks[2])
