from datetime import date, timedelta

import pytest
from init_db_tests import init_db

from django.test import TestCase
from maintenancemanagement.models import Field, FieldObject, Task
from utils.trigger_tasks import (
    at_least_one_conditon_is_verified,
    check_tasks,
    condition_is_verified,
)


class TaskAutoTriggerTests(TestCase):

    @pytest.fixture(scope="class", autouse=True)
    def init_database(django_db_setup, django_db_blocker):
        with django_db_blocker.unblock():
            init_db()

    def test_US22_I1_condition_is_verified_recurrence(self):
        """
            Test if a recurrence trigger condition is verified.

            Inputs:
                task (Task): a task to check if recurrence trigger conditions are verified.
                field_object_verified (FieldObject): a verified recurrence trigger condition.
                field_object_not_yet_verified (FieldObject): a not yet verified recurrence trigger condition.

            Expected Output:
                We expect to have the field_object_verified verified.
                We expect to not have the field_object_not_yet_verified verified.
        """
        task = Task.objects.create(name='Task', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        field_object_verified = FieldObject.objects.create(
            described_object=task, field=Field.objects.get(name="Recurrence"), value="30d|5d"
        )
        field_object_not_yet_verified = FieldObject.objects.create(
            described_object=task, field=Field.objects.get(name="Recurrence"), value="30d|4d"
        )
        self.assertTrue(condition_is_verified(field_object_verified, task))
        self.assertFalse(condition_is_verified(field_object_not_yet_verified, task))

    def test_US22_I1_condition_is_verified_above_threshold(self):
        """
            Test if an above threshold trigger condition is verified.

            Inputs:
                task (Task): a task to check if an above threshold trigger conditions are verified.
                field_object_verified (FieldObject): a verified an above threshold trigger condition.
                field_object_not_yet_verified (FieldObject): a not yet verified an above threshold trigger condition.

            Expected Output:
                We expect to have the field_object_verified verified.
                We expect to not have the field_object_not_yet_verified verified.
        """
        task = Task.objects.create(name='Task', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        related_field_object = FieldObject.objects.get(field=Field.objects.get(name="Nb bouteilles"))
        field_object_verified = FieldObject.objects.create(
            described_object=task,
            field=Field.objects.get(name="Above Threshold"),
            value=f"40000|{related_field_object.id}|7d"
        )
        field_object_not_yet_verified = FieldObject.objects.create(
            described_object=task,
            field=Field.objects.get(name="Above Threshold"),
            value=f"60000|{related_field_object.id}|7d"
        )
        self.assertTrue(condition_is_verified(field_object_verified, task))
        self.assertFalse(condition_is_verified(field_object_not_yet_verified, task))

    def test_US22_I1_condition_is_verified_under_threshold(self):
        """
            Test if an under threshold trigger condition is verified.

            Inputs:
                task (Task): a task to check if an under threshold trigger conditions are verified.
                field_object_verified (FieldObject): a verified an under threshold trigger condition.
                field_object_not_yet_verified (FieldObject): a not yet verified an under threshold trigger condition.

            Expected Output:
                We expect to have the field_object_verified verified.
                We expect to not have the field_object_not_yet_verified verified.
        """
        task = Task.objects.create(name='Task', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        related_field_object = FieldObject.objects.get(field=Field.objects.get(name="Nb bouteilles"))
        field_object_verified = FieldObject.objects.create(
            described_object=task,
            field=Field.objects.get(name="Under Threshold"),
            value=f"60000|{related_field_object.id}|7d"
        )
        field_object_not_yet_verified = FieldObject.objects.create(
            described_object=task,
            field=Field.objects.get(name="Under Threshold"),
            value=f"40000|{related_field_object.id}|7d"
        )
        self.assertTrue(condition_is_verified(field_object_verified, task))
        self.assertFalse(condition_is_verified(field_object_not_yet_verified, task))

    def test_US22_I1_condition_is_verified_frequency(self):
        """
            Test if a frequency trigger condition is verified.

            Inputs:
                task (Task): a task to check if frequency trigger conditions are verified.
                field_object_verified (FieldObject): a verified frequency trigger condition.
                field_object_not_yet_verified (FieldObject): a not yet verified frequency trigger condition.

            Expected Output:
                We expect to have the field_object_verified verified.
                We expect to not have the field_object_not_yet_verified verified.
        """
        task = Task.objects.create(name='Task', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        related_field_object = FieldObject.objects.get(field=Field.objects.get(name="Nb bouteilles"))
        field_object_verified = FieldObject.objects.create(
            described_object=task,
            field=Field.objects.get(name="Frequency"),
            value=f"10000|{related_field_object.id}|7d|50000"
        )
        field_object_not_yet_verified = FieldObject.objects.create(
            described_object=task,
            field=Field.objects.get(name="Frequency"),
            value=f"10000|{related_field_object.id}|7d|60000"
        )
        self.assertTrue(condition_is_verified(field_object_verified, task))
        self.assertFalse(condition_is_verified(field_object_not_yet_verified, task))

    def test_US22_I1_at_least_one_conditon_is_verified(self):
        """
            Test if at leats one condition is verified for a task.

            Inputs:
                task_1 (Task): a task with at leats one trigger condition verified.
                task_2 (Task): a task without at leats one trigger condition verified.
                task_3 (Task): a task without at leats one trigger condition verified.
                task_4 (Task): a task with at leats one trigger condition verified.
                task_5 (Task): a task with at leats one trigger condition verified.

            Expected Output:
                We expect to find that task_1, task_4 and task_5 have at least one trigger condition verified.
                We expect to find that task_2 and task_3 have not at least one trigger condition verified.
        """
        related_field_object = FieldObject.objects.get(field=Field.objects.get(name="Nb bouteilles"))
        task_1 = Task.objects.create(name='Task', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        FieldObject.objects.create(described_object=task_1, field=Field.objects.get(name="Recurrence"), value="30d|5d")
        task_2 = Task.objects.create(name='Task', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        FieldObject.objects.create(
            described_object=task_2,
            field=Field.objects.get(name="Above Threshold"),
            value=f"60000|{related_field_object.id}|7d"
        )
        task_3 = Task.objects.create(name='Task', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        FieldObject.objects.create(
            described_object=task_3,
            field=Field.objects.get(name="Under Threshold"),
            value=f"40000|{related_field_object.id}|7d"
        )
        FieldObject.objects.create(
            described_object=task_3,
            field=Field.objects.get(name="Frequency"),
            value=f"10000|{related_field_object.id}|7d|60000"
        )
        task_4 = Task.objects.create(name='Task', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        FieldObject.objects.create(described_object=task_4, field=Field.objects.get(name="Recurrence"), value="30d|4d")
        FieldObject.objects.create(
            described_object=task_4,
            field=Field.objects.get(name="Above Threshold"),
            value=f"40000|{related_field_object.id}|7d"
        )
        task_5 = Task.objects.create(name='Task', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        FieldObject.objects.create(
            described_object=task_5,
            field=Field.objects.get(name="Frequency"),
            value=f"10000|{related_field_object.id}|7d|50000"
        )
        FieldObject.objects.create(described_object=task_5, field=Field.objects.get(name="Recurrence"), value="30d|5d")
        FieldObject.objects.create(
            described_object=task_5,
            field=Field.objects.get(name="Under Threshold"),
            value=f"60000|{related_field_object.id}|7d"
        )
        self.assertTrue(at_least_one_conditon_is_verified(task_1))
        self.assertFalse(at_least_one_conditon_is_verified(task_2))
        self.assertFalse(at_least_one_conditon_is_verified(task_3))
        self.assertTrue(at_least_one_conditon_is_verified(task_4))
        self.assertTrue(at_least_one_conditon_is_verified(task_5))

    def test_US22_I2_check_tasks_trigger_task(self):
        """
            Test if a task is triggered by check_tasks.

            Inputs:
                task_1 (Task): a task with at leats one trigger condition verified.
                task_2 (Task): a task without at leats one trigger condition verified.
                task_3 (Task): a task without at leats one trigger condition verified.
                task_4 (Task): a task with at leats one trigger condition verified.
                task_5 (Task): a task with at leats one trigger condition verified.

            Expected Output:
                We expect to find that task_1, task_4 and task_5 are triggered.
                We expect to find that task_2 and task_3 are not triggered.
        """
        related_field_object = FieldObject.objects.get(field=Field.objects.get(name="Nb bouteilles"))
        task_1 = Task.objects.create(name='Task 1', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        FieldObject.objects.create(described_object=task_1, field=Field.objects.get(name="Recurrence"), value="30d|5d")
        task_2 = Task.objects.create(name='Task 2', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        FieldObject.objects.create(
            described_object=task_2,
            field=Field.objects.get(name="Above Threshold"),
            value=f"60000|{related_field_object.id}|7d"
        )
        task_3 = Task.objects.create(name='Task 3', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        FieldObject.objects.create(
            described_object=task_3,
            field=Field.objects.get(name="Under Threshold"),
            value=f"40000|{related_field_object.id}|7d"
        )
        FieldObject.objects.create(
            described_object=task_3,
            field=Field.objects.get(name="Frequency"),
            value=f"10000|{related_field_object.id}|7d|60000"
        )
        task_4 = Task.objects.create(name='Task 4', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        FieldObject.objects.create(described_object=task_4, field=Field.objects.get(name="Recurrence"), value="30d|4d")
        FieldObject.objects.create(
            described_object=task_4,
            field=Field.objects.get(name="Above Threshold"),
            value=f"40000|{related_field_object.id}|7d"
        )
        task_5 = Task.objects.create(name='Task 5', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        FieldObject.objects.create(
            described_object=task_5,
            field=Field.objects.get(name="Frequency"),
            value=f"10000|{related_field_object.id}|7d|50000"
        )
        FieldObject.objects.create(described_object=task_5, field=Field.objects.get(name="Recurrence"), value="30d|5d")
        FieldObject.objects.create(
            described_object=task_5,
            field=Field.objects.get(name="Under Threshold"),
            value=f"60000|{related_field_object.id}|7d"
        )
        check_tasks()
        self.assertTrue(Task.objects.get(name="Task 1").is_triggered)
        self.assertFalse(Task.objects.get(name="Task 2").is_triggered)
        self.assertFalse(Task.objects.get(name="Task 3").is_triggered)
        self.assertTrue(Task.objects.get(name="Task 4").is_triggered)
        self.assertTrue(Task.objects.get(name="Task 5").is_triggered)

    def test_US22_I2_check_tasks_update_end_date(self):
        """
            Test if the end_date of a task is updated by check_tasks.

            Inputs:
                task_1 (Task): a task with a frequency trigger condition verified.
                task_2 (Task): a task with an above threshold trigger condition verified.
                task_3 (Task): a task with an under threshold trigger condition verified.
                
            Expected Output:
                We expect to find that task_1, task_2 and task_3 have good end_date after beeing triggered.
        """
        related_field_object = FieldObject.objects.get(field=Field.objects.get(name="Nb bouteilles"))
        task_1 = Task.objects.create(name='Task 1', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        FieldObject.objects.create(
            described_object=task_1,
            field=Field.objects.get(name="Frequency"),
            value=f"10000|{related_field_object.id}|3d|50000"
        )
        task_2 = Task.objects.create(name='Task 2', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        FieldObject.objects.create(
            described_object=task_2,
            field=Field.objects.get(name="Above Threshold"),
            value=f"40000|{related_field_object.id}|5d"
        )
        task_3 = Task.objects.create(name='Task 3', end_date=(date.today() + timedelta(days=5)), is_triggered=False)
        FieldObject.objects.create(
            described_object=task_3,
            field=Field.objects.get(name="Under Threshold"),
            value=f"60000|{related_field_object.id}|7d"
        )
        check_tasks()
        self.assertEqual(Task.objects.get(name="Task 1").end_date, date.today() + timedelta(days=3))
        self.assertEqual(Task.objects.get(name="Task 2").end_date, date.today() + timedelta(days=5))
        self.assertEqual(Task.objects.get(name="Task 3").end_date, date.today() + timedelta(days=7))
