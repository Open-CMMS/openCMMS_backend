from datetime import date, timedelta
from io import BytesIO

import pytest
from init_db_tests import init_db

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from maintenancemanagement.models import (
    Field,
    FieldGroup,
    FieldObject,
    FieldValue,
    File,
    Task,
)
from maintenancemanagement.serializers import (
    EquipmentTypeSerializer,
    FileSerializer,
    TaskListingSerializer,
    TaskSerializer,
    TeamSerializer,
)
from openCMMS import settings
from rest_framework.test import APIClient
from usersmanagement.models import Team, TeamType, UserProfile
from utils.methods import parse_time

User = settings.AUTH_USER_MODEL


class TaskTests(TestCase):

    @pytest.fixture(scope="class", autouse=True)
    def init_database(django_db_setup, django_db_blocker):
        with django_db_blocker.unblock():
            init_db()

    def set_up_perm(self):
        """
            Set up a user with permissions
        """
        permission = Permission.objects.get(codename='add_task')
        permission2 = Permission.objects.get(codename='view_task')
        permission3 = Permission.objects.get(codename='delete_task')
        permission4 = Permission.objects.get(codename='change_task')

        user = UserProfile.objects.create(username='tom')
        user.set_password('truc')
        user.first_name = 'Tom'
        user.save()

        user.user_permissions.add(permission)
        user.user_permissions.add(permission2)
        user.user_permissions.add(permission3)
        user.user_permissions.add(permission4)

        user.save()

        return user

    def set_up_without_perm(self):
        """
            Set up a user without permissions
        """
        user = UserProfile.objects.create(username='tomy')
        user.set_password('truc')
        user.first_name = 'Tom'
        user.save()
        return user

    def test_US22_I1_with_recurrence(self):
        """
        docstring
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        trigger_conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="Trigger Conditions"))
        # field_object = FieldObject.objects.get(field=Field.objects.get(name="Nb bouteilles"))
        # nb_bouteilles_value = float(field_object.value)
        end_conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="End Conditions"))
        client.post(
            '/api/maintenancemanagement/tasks/',
            {
                'name':
                    'verifier pneus',
                'description':
                    'desc_task_test_create_task_with_perm_with_trigger_conditions',
                'trigger_conditions':
                    [
                        {
                            "field": trigger_conditions.get(name="Recurrence").id,
                            "value": "30d",
                            "delay": "7d",
                            "description": "test_create_task_with_perm_with_trigger_conditions_recurrence"
                        }
                        # {
                        # 'field': trigger_conditions.get(name='Above Threshold').id,
                        # 'value': '0.6',
                        # 'field_object_id': field_object.id,
                        # 'delay': '2d',
                        # 'description': 'test_add_task_with_perm_with_trigger_conditions_above_threshold'
                        # }, {
                        # 'field': trigger_conditions.get(name='Under Threshold').id,
                        # 'value': '0.6',
                        # 'field_object_id': field_object.id,
                        # 'delay': '2d',
                        # 'description': 'test_add_task_with_perm_with_trigger_conditions_under_threshold'
                        # }, {
                        # 'field': trigger_conditions.get(name='Frequency').id,
                        # 'value': '10000',
                        # 'field_object_id': field_object.id,
                        # 'delay': '2d',
                        # 'description': 'test_add_task_with_perm_with_trigger_conditions_frequency'
                        # }
                    ],
                'end_conditions':
                    [
                        {
                            "field": end_conditions.get(name="Checkbox").id,
                            "value": "false",
                            "description": "test_add_task_with_perm_with_end_conditions_1"
                        }
                    ]
            },
            format='json'
        )
        task = Task.objects.get(name='verifier pneus')
        response = client.put(
            f'/api/maintenancemanagement/tasks/{task.id}/', {
                'end_conditions':
                    [
                        {
                            "field": FieldObject.objects.get(field=end_conditions.get(name="Checkbox")).id,
                            "value": "true",
                            "description": "test_add_task_with_perm_with_end_conditions_1"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        tasks = Task.objects.filter(name='verifier pneus')
        self.assertEqual(tasks.count(), 2)
        self.assertEqual(tasks.filter(over='True').count(), 1)
        self.assertEqual(tasks.filter(over='False').count(), 1)
        self.assertEqual(tasks.filter(over='False')[0].end_date, date.today() + parse_time('30d'))
        self.assertEqual(tasks[0].name, tasks[1].name)
        self.assertEqual(tasks[0].description, tasks[1].description)
        self.assertEqual(tasks[0].created_by, tasks[1].created_by)
        self.assertEqual(tasks[0].equipment, tasks[1].equipment)
        self.assertEqual(tasks[0].duration, tasks[1].duration)
        teams0 = tasks[0].teams.filter()
        teams1 = tasks[1].teams.filter()
        self.assertEqual(len(teams0), len(teams1))
        for team0, team1 in zip(teams0, teams1):
            self.assertEqual(team0, team1)

    def test_US22_I1_with_frequency(self):
        """
        docstring
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        trigger_conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="Trigger Conditions"))
        field_object = FieldObject.objects.get(field=Field.objects.get(name="Nb bouteilles"))
        nb_bouteilles_value = float(field_object.value)
        end_conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="End Conditions"))
        client.post(
            '/api/maintenancemanagement/tasks/',
            {
                'name':
                    'verifier pneus',
                'description':
                    'desc_task_test_create_task_with_perm_with_trigger_conditions',
                'trigger_conditions':
                    [
                        # {
                        #     "field": trigger_conditions.get(name="Recurrence").id,
                        #     "value": "50d",
                        #     "delay": "7d",
                        #     "description": "test_create_task_with_perm_with_trigger_conditions_frequency"
                        # }
                        # {
                        # 'field': trigger_conditions.get(name='Above Threshold').id,
                        # 'value': '0.6',
                        # 'field_object_id': field_object.id,
                        # 'delay': '2d',
                        # 'description': 'test_add_task_with_perm_with_trigger_conditions_above_threshold'
                        # },
                        # {
                        # 'field': trigger_conditions.get(name='Under Threshold').id,
                        # 'value': '0.6',
                        # 'field_object_id': field_object.id,
                        # 'delay': '2d',
                        # 'description': 'test_add_task_with_perm_with_trigger_conditions_under_threshold'
                        # },
                        {
                            'field': trigger_conditions.get(name='Frequency').id,
                            'value': '10000',
                            'field_object_id': field_object.id,
                            'delay': '2d',
                            'description': 'test_add_task_with_perm_with_trigger_conditions_frequency'
                        }
                    ],
                'end_conditions':
                    [
                        {
                            "field": end_conditions.get(name="Checkbox").id,
                            "value": "",
                            "description": "test_add_task_with_perm_with_end_conditions_1"
                        }
                    ]
            },
            format='json'
        )
        task = Task.objects.get(name='verifier pneus')
        response = client.put(
            f'/api/maintenancemanagement/tasks/{task.id}/', {
                'end_conditions':
                    [
                        {
                            "field": FieldObject.objects.get(field=end_conditions.get(name="Checkbox")).id,
                            "value": "True",
                            "description": "test_add_task_with_perm_with_end_conditions_1"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        tasks = Task.objects.filter(name='verifier pneus')
        self.assertEqual(tasks.count(), 2)
        self.assertEqual(tasks.filter(over='True').count(), 1)
        self.assertEqual(tasks.filter(over='False').count(), 1)
        content_type_object = ContentType.objects.get_for_model(tasks.get(over='False'))
        condition = FieldObject.objects.filter(
            object_id=task.id,
            content_type=content_type_object,
            field__field_group__name='Trigger Conditions',
            field__name='Frequency'
        )[0]
        self.assertEqual(float(condition.value.split('|')[3]), nb_bouteilles_value + 10000)
        self.assertEqual(tasks[0].name, tasks[1].name)
        self.assertEqual(tasks[0].description, tasks[1].description)
        self.assertEqual(tasks[0].created_by, tasks[1].created_by)
        self.assertEqual(tasks[0].equipment, tasks[1].equipment)
        self.assertEqual(tasks[0].duration, tasks[1].duration)
        teams0 = tasks[0].teams.filter()
        teams1 = tasks[1].teams.filter()
        self.assertEqual(len(teams0), len(teams1))
        for team0, team1 in zip(teams0, teams1):
            self.assertEqual(team0, team1)
        self.assertIsNone(tasks[1].end_date)

    def test_US22_I1_with_above_thresohld(self):
        """
        docstring
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        trigger_conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="Trigger Conditions"))
        field_object = FieldObject.objects.get(field=Field.objects.get(name="Nb bouteilles"))
        #nb_bouteilles_value = float(field_object.value)
        end_conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="End Conditions"))
        client.post(
            '/api/maintenancemanagement/tasks/',
            {
                'name':
                    'verifier pneus',
                'description':
                    'desc_task_test_create_task_with_perm_with_trigger_conditions',
                'trigger_conditions':
                    [
                        # {
                        #     "field": trigger_conditions.get(name="Frequency").id,
                        #     "value": "50",
                        #     "delay": "7d",
                        #     "description": "test_create_task_with_perm_with_trigger_conditions_frequency"
                        # }
                        {
                            'field': trigger_conditions.get(name='Above Threshold').id,
                            'value': '0.6',
                            'field_object_id': field_object.id,
                            'delay': '2d',
                            'description': 'test_add_task_with_perm_with_trigger_conditions_above_threshold'
                        },
                        # {
                        # 'field': trigger_conditions.get(name='Under Threshold').id,
                        # 'value': '0.6',
                        # 'field_object_id': field_object.id,
                        # 'delay': '2d',
                        # 'description': 'test_add_task_with_perm_with_trigger_conditions_under_threshold'
                        # },
                        # {
                        #     'field': trigger_conditions.get(name='Frequency').id,
                        #     'value': '10000',
                        #     'field_object_id': field_object.id,
                        #     'delay': '2d',
                        #     'description': 'test_add_task_with_perm_with_trigger_conditions_frequency'
                        # }
                    ],
                'end_conditions':
                    [
                        {
                            "field": end_conditions.get(name="Checkbox").id,
                            "value": "",
                            "description": "test_add_task_with_perm_with_end_conditions_1"
                        }
                    ]
            },
            format='json'
        )
        task = Task.objects.get(name='verifier pneus')
        response = client.put(
            f'/api/maintenancemanagement/tasks/{task.id}/', {
                'end_conditions':
                    [
                        {
                            "field": FieldObject.objects.get(field=end_conditions.get(name="Checkbox")).id,
                            "value": "True",
                            "description": "test_add_task_with_perm_with_end_conditions_1"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        tasks = Task.objects.filter(name='verifier pneus')
        self.assertEqual(tasks.count(), 2)
        self.assertEqual(tasks.filter(over='True').count(), 1)
        self.assertEqual(tasks.filter(over='False').count(), 1)
        self.assertEqual(tasks[0].name, tasks[1].name)
        self.assertEqual(tasks[0].description, tasks[1].description)
        self.assertEqual(tasks[0].created_by, tasks[1].created_by)
        self.assertEqual(tasks[0].equipment, tasks[1].equipment)
        self.assertEqual(tasks[0].duration, tasks[1].duration)
        teams0 = tasks[0].teams.filter()
        teams1 = tasks[1].teams.filter()
        self.assertEqual(len(teams0), len(teams1))
        for team0, team1 in zip(teams0, teams1):
            self.assertEqual(team0, team1)
        self.assertIsNone(tasks[1].end_date)

    def test_US22_I1_with_under_threshold(self):
        """
        docstring
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        trigger_conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="Trigger Conditions"))
        field_object = FieldObject.objects.get(field=Field.objects.get(name="Nb bouteilles"))
        #nb_bouteilles_value = float(field_object.value)
        end_conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="End Conditions"))
        client.post(
            '/api/maintenancemanagement/tasks/',
            {
                'name':
                    'verifier pneus',
                'description':
                    'desc_task_test_create_task_with_perm_with_trigger_conditions',
                'trigger_conditions':
                    [
                        # {
                        #     "field": trigger_conditions.get(name="Frequency").id,
                        #     "value": "50",
                        #     "delay": "7d",
                        #     "description": "test_create_task_with_perm_with_trigger_conditions_frequency"
                        # }
                        # {
                        #     'field': trigger_conditions.get(name='Above Threshold').id,
                        #     'value': '0.6',
                        #     'field_object_id': field_object.id,
                        #     'delay': '2d',
                        #     'description': 'test_add_task_with_perm_with_trigger_conditions_above_threshold'
                        # },
                        {
                            'field': trigger_conditions.get(name='Under Threshold').id,
                            'value': '0.6',
                            'field_object_id': field_object.id,
                            'delay': '2d',
                            'description': 'test_add_task_with_perm_with_trigger_conditions_under_threshold'
                        },
                        # {
                        #     'field': trigger_conditions.get(name='Frequency').id,
                        #     'value': '10000',
                        #     'field_object_id': field_object.id,
                        #     'delay': '2d',
                        #     'description': 'test_add_task_with_perm_with_trigger_conditions_frequency'
                        # }
                    ],
                'end_conditions':
                    [
                        {
                            "field": end_conditions.get(name="Checkbox").id,
                            "value": "",
                            "description": "test_add_task_with_perm_with_end_conditions_1"
                        }
                    ]
            },
            format='json'
        )
        task = Task.objects.get(name='verifier pneus')
        response = client.put(
            f'/api/maintenancemanagement/tasks/{task.id}/', {
                'end_conditions':
                    [
                        {
                            "field": FieldObject.objects.get(field=end_conditions.get(name="Checkbox")).id,
                            "value": "True",
                            "description": "test_add_task_with_perm_with_end_conditions_1"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        tasks = Task.objects.filter(name='verifier pneus')
        self.assertEqual(tasks.count(), 2)
        self.assertEqual(tasks.filter(over='True').count(), 1)
        self.assertEqual(tasks.filter(over='False').count(), 1)
        self.assertEqual(tasks[0].name, tasks[1].name)
        self.assertEqual(tasks[0].description, tasks[1].description)
        self.assertEqual(tasks[0].created_by, tasks[1].created_by)
        self.assertEqual(tasks[0].equipment, tasks[1].equipment)
        self.assertEqual(tasks[0].duration, tasks[1].duration)
        teams0 = tasks[0].teams.filter()
        teams1 = tasks[1].teams.filter()
        self.assertEqual(len(teams0), len(teams1))
        for team0, team1 in zip(teams0, teams1):
            self.assertEqual(team0, team1)
        self.assertIsNone(tasks[1].end_date)

    def test_US22_I1_with_under_threshold_and_frequency(self):
        """
        docstring
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        trigger_conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="Trigger Conditions"))
        field_object = FieldObject.objects.get(field=Field.objects.get(name="Nb bouteilles"))
        nb_bouteilles_value = float(field_object.value)
        end_conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="End Conditions"))
        client.post(
            '/api/maintenancemanagement/tasks/',
            {
                'name':
                    'verifier pneus',
                'description':
                    'desc_task_test_create_task_with_perm_with_trigger_conditions',
                'trigger_conditions':
                    [
                        # {
                        #     "field": trigger_conditions.get(name="Recurrence").id,
                        #     "value": "50d",
                        #     "delay": "7d",
                        #     "description": "test_create_task_with_perm_with_trigger_conditions_frequency",
                        # },
                        # {
                        #     'field': trigger_conditions.get(name='Above Threshold').id,
                        #     'value': '0.6',
                        #     'field_object_id': field_object.id,
                        #     'delay': '2d',
                        #     'description': 'test_add_task_with_perm_with_trigger_conditions_above_threshold'
                        # },
                        {
                            'field': trigger_conditions.get(name='Under Threshold').id,
                            'value': '0.6',
                            'field_object_id': field_object.id,
                            'delay': '2d',
                            'description': 'test_add_task_with_perm_with_trigger_conditions_under_threshold'
                        },
                        {
                            'field': trigger_conditions.get(name='Frequency').id,
                            'value': '10000',
                            'field_object_id': field_object.id,
                            'delay': '2d',
                            'description': 'test_add_task_with_perm_with_trigger_conditions_frequency'
                        }
                    ],
                'end_conditions':
                    [
                        {
                            "field": end_conditions.get(name="Checkbox").id,
                            "value": "",
                            "description": "test_add_task_with_perm_with_end_conditions_1"
                        }
                    ]
            },
            format='json'
        )
        task = Task.objects.get(name='verifier pneus')
        response = client.put(
            f'/api/maintenancemanagement/tasks/{task.id}/', {
                'end_conditions':
                    [
                        {
                            "field": FieldObject.objects.get(field=end_conditions.get(name="Checkbox")).id,
                            "value": "True",
                            "description": "test_add_task_with_perm_with_end_conditions_1"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        tasks = Task.objects.filter(name='verifier pneus')
        self.assertEqual(tasks.count(), 2)
        self.assertEqual(tasks.filter(over='True').count(), 1)
        self.assertEqual(tasks.filter(over='False').count(), 1)
        content_type_object = ContentType.objects.get_for_model(tasks.get(over='False'))
        condition = FieldObject.objects.filter(
            object_id=task.id,
            content_type=content_type_object,
            field__field_group__name='Trigger Conditions',
            field__name='Frequency'
        )[0]
        self.assertEqual(float(condition.value.split('|')[3]), nb_bouteilles_value + 10000)
        self.assertEqual(tasks[0].name, tasks[1].name)
        self.assertEqual(tasks[0].name, tasks[1].name)
        self.assertEqual(tasks[0].description, tasks[1].description)
        self.assertEqual(tasks[0].created_by, tasks[1].created_by)
        self.assertEqual(tasks[0].equipment, tasks[1].equipment)
        self.assertEqual(tasks[0].duration, tasks[1].duration)
        teams0 = tasks[0].teams.filter()
        teams1 = tasks[1].teams.filter()
        self.assertEqual(len(teams0), len(teams1))
        for team0, team1 in zip(teams0, teams1):
            self.assertEqual(team0, team1)
        self.assertIsNone(tasks[1].end_date)

    def test_US22_I1_with_recurrence_and_frequency(self):
        """
        docstring
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        trigger_conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="Trigger Conditions"))
        field_object = FieldObject.objects.get(field=Field.objects.get(name="Nb bouteilles"))
        nb_bouteilles_value = float(field_object.value)
        end_conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="End Conditions"))
        client.post(
            '/api/maintenancemanagement/tasks/',
            {
                'name':
                    'verifier pneus',
                'description':
                    'desc_task_test_create_task_with_perm_with_trigger_conditions',
                'trigger_conditions':
                    [
                        {
                            "field": trigger_conditions.get(name="Recurrence").id,
                            "value": "50d",
                            "delay": "7d",
                            "description": "test_create_task_with_perm_with_trigger_conditions_frequency",
                        },
                        # {
                        #     'field': trigger_conditions.get(name='Above Threshold').id,
                        #     'value': '0.6',
                        #     'field_object_id': field_object.id,
                        #     'delay': '2d',
                        #     'description': 'test_add_task_with_perm_with_trigger_conditions_above_threshold'
                        # },
                        # {
                        #     'field': trigger_conditions.get(name='Under Threshold').id,
                        #     'value': '0.6',
                        #     'field_object_id': field_object.id,
                        #     'delay': '2d',
                        #     'description': 'test_add_task_with_perm_with_trigger_conditions_under_threshold'
                        # },
                        {
                            'field': trigger_conditions.get(name='Frequency').id,
                            'value': '10000',
                            'field_object_id': field_object.id,
                            'delay': '2d',
                            'description': 'test_add_task_with_perm_with_trigger_conditions_frequency'
                        }
                    ],
                'end_conditions':
                    [
                        {
                            "field": end_conditions.get(name="Checkbox").id,
                            "value": "",
                            "description": "test_add_task_with_perm_with_end_conditions_1"
                        }
                    ]
            },
            format='json'
        )
        task = Task.objects.get(name='verifier pneus')
        response = client.put(
            f'/api/maintenancemanagement/tasks/{task.id}/', {
                'end_conditions':
                    [
                        {
                            "field": FieldObject.objects.get(field=end_conditions.get(name="Checkbox")).id,
                            "value": "True",
                            "description": "test_add_task_with_perm_with_end_conditions_1"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        tasks = Task.objects.filter(name='verifier pneus')
        self.assertEqual(tasks.count(), 2)
        self.assertEqual(tasks.filter(over='True').count(), 1)
        self.assertEqual(tasks.filter(over='False').count(), 1)
        content_type_object = ContentType.objects.get_for_model(tasks.get(over='False'))
        condition = FieldObject.objects.filter(
            object_id=task.id,
            content_type=content_type_object,
            field__field_group__name='Trigger Conditions',
            field__name='Frequency'
        )[0]
        self.assertEqual(float(condition.value.split('|')[3]), nb_bouteilles_value + 10000)
        self.assertEqual(tasks[0].name, tasks[1].name)
        self.assertEqual(tasks[0].name, tasks[1].name)
        self.assertEqual(tasks[0].description, tasks[1].description)
        self.assertEqual(tasks[0].created_by, tasks[1].created_by)
        self.assertEqual(tasks[0].equipment, tasks[1].equipment)
        self.assertEqual(tasks[0].duration, tasks[1].duration)
        teams0 = tasks[0].teams.filter()
        teams1 = tasks[1].teams.filter()
        self.assertEqual(len(teams0), len(teams1))
        for team0, team1 in zip(teams0, teams1):
            self.assertEqual(team0, team1)
        self.assertEqual(tasks.filter(over='False')[0].end_date, date.today() + parse_time('50d'))
