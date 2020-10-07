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
        task1.teams.add(team)
        task1.save()
        task2.teams.add(team)
        task2.save()
        task3.teams.add(team)
        task3.save()
        team.user_set.add(joe)
        team.save()

    def test_US17_I1_send_notification_user_with_task(self):
        self.set_up()
        send_notifications()
        # os.mkdir()
        with open('/tmp/mails', 'w') as f:
            for email in mail.outbox:
                f.write(str(email.body))
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Notification Open-CMMS')
        self.assertEqual(email.to[0], 'joe.d@ll.com')
        self.assertEqual(1, len(email.to))
