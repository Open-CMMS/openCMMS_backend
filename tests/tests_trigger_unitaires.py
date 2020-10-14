from datetime import date, timedelta

from django.test import TestCase
from maintenancemanagement.models import Field, FieldGroup, FieldObject, Task
from utils.triggers import activate_triggered_tasks, task_is_triggered


class TaskTriggerTests(TestCase):
    """
        Tests for task triggered conditions.
    """

    def set_up(self):
        date_condition = Field.objects.get(name='Date')

        task_to_trigger_yesterday = Task.objects.create(name='task_yesterday', over=None)
        FieldObject.objects.create(
            field=date_condition,
            described_object=task_to_trigger_yesterday,
            value=str(date.today() - timedelta(days=1))
        )
        task_to_trigger_today = Task.objects.create(name='task_today', over=None)
        FieldObject.objects.create(
            field=date_condition, described_object=task_to_trigger_today, value=str(date.today())
        )
        task_to_trigger_tomorrow = Task.objects.create(name='task_tomorrow', over=None)
        FieldObject.objects.create(
            field=date_condition,
            described_object=task_to_trigger_tomorrow,
            value=str(date.today() + timedelta(days=1))
        )

    def test_US22_U1_task_is_triggered_with_passed_conditon(self):
        self.set_up()
        self.assertTrue(task_is_triggered(Task.objects.get(name='task_yesterday')))

    def test_US22_U2_task_is_triggered_with_today_conditon(self):
        self.set_up()
        self.assertTrue(task_is_triggered(Task.objects.get(name='task_today')))

    def test_US22_U3_task_is_triggered_with_future_conditon(self):
        self.set_up()
        self.assertFalse(task_is_triggered(Task.objects.get(name='task_tomorrow')))

    def test_US22_U4_activate_triggered_tasks(self):
        self.set_up()
        activate_triggered_tasks()
        self.assertIsNotNone(Task.objects.get(name='task_yesterday').over)
        self.assertIsNotNone(Task.objects.get(name='task_today').over)
        self.assertIsNone(Task.objects.get(name='task_tomorrow').over)
