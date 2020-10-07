from datetime import timedelta

from django.contrib.auth.models import Permission
from django.test import TestCase
from maintenancemanagement.models import (
    Field,
    FieldGroup,
    FieldObject,
    FieldValue,
    Task,
)
from maintenancemanagement.serializers import TaskSerializer
from openCMMS import settings
from rest_framework.test import APIClient
from usersmanagement.models import Team, TeamType, UserProfile

User = settings.AUTH_USER_MODEL


class TaskTests(TestCase):

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
        user = UserProfile.objects.create(username='tom')
        user.set_password('truc')
        user.first_name = 'Tom'
        user.save()
        return user

    def temporary_file(self):
        """
        Returns a new temporary file
        """
        import tempfile
        tmp_file = tempfile.TemporaryFile()
        tmp_file.write(b'Coco veut un gateau')
        tmp_file.seek(0)
        return tmp_file

    def add_add_perm_file(self, user):
        """
            Add add permission for file
        """
        permission = Permission.objects.get(codename='add_file')
        user.user_permissions.add(permission)

    def test_US5_I1_tasklist_get_with_perm(self):
        """
            Test if a user with perm receive the data
        """
        user = self.set_up_perm()
        tasks = Task.objects.filter(is_template=False)
        serializer = TaskSerializer(tasks, many=True)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/', format='json')
        self.assertEqual(response.data, serializer.data)

    def test_US5_I1_tasklist_get_without_perm(self):
        """
            Test if a user without perm doesn't receive the data
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/', format='json')
        self.assertEqual(response.status_code, 401)

    def test_US5_I2_tasklist_post_with_perm(self):
        """
            Test if a user with perm can add a task
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'verifier pneus')

    def test_US5_I2_tasklist_post_without_perm(self):
        """
            Test if a user without perm can't add a task
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_US5_I3_taskdetail_get_with_perm(self):
        """
            Test if a user with perm can see a task detail
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu'
            },
            format='json'
        )
        pk = response1.data['id']
        response = client.get('/api/maintenancemanagement/tasks/' + str(pk) + '/')
        self.assertEqual(response.data['name'], 'verifier pneus')

    def test_US5_I3_taskdetail_get_without_perm(self):
        """
            Test if a user without perm can't see a task detail
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu'
            },
            format='json'
        )
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/' + str(pk) + '/')
        self.assertEqual(response.status_code, 401)

    def test_US5_I4_taskdetail_put_with_perm(self):
        """
            Test if a user with perm can change a task
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu'
            },
            format='json'
        )
        pk = response1.data['id']
        response = client.put(
            '/api/maintenancemanagement/tasks/' + str(pk) + '/', {'name': 'verifier roues'}, format='json'
        )
        self.assertEqual(response.data['name'], 'verifier roues')
        self.assertEqual(response.status_code, 200)

    def test_US5_I4_taskdetail_put_without_perm(self):
        """
            Test if a user without perm can change a task
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu'
            },
            format='json'
        )
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.put(
            '/api/maintenancemanagement/tasks/' + str(pk) + '/', {'name': 'verifier roues'}, format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_US5_I5_taskdetail_delete_with_perm(self):
        """
            Test if a user with perm can delete a task
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu'
            },
            format='json'
        )
        pk = response1.data['id']
        response = client.delete('/api/maintenancemanagement/tasks/' + str(pk) + '/')
        self.assertEqual(response.status_code, 204)

    def test_US5_I5_taskdetail_delete_without_perm(self):
        """
            Test if a user without perm can delete a task
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu'
            },
            format='json'
        )
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.delete('/api/maintenancemanagement/tasks/' + str(pk) + '/')
        self.assertEqual(response.status_code, 401)

    def test_US6_I1_addteamtotask_post_with_perm(self):
        """
            Test if a user with permission can add a team to a task.
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        team = Team.objects.create(name="team")
        task = Task.objects.create(name="tache")
        response = client.post(
            '/api/maintenancemanagement/add_team_to_task/', {
                "id_team": f"{team.pk}",
                "id_task": f"{task.pk}"
            },
            format="json"
        )
        self.assertEqual(response.status_code, 201)

    def test_US6_I1_addteamtotask_put_with_perm(self):
        """
            Test if a user with permission can remove a team from a task.
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        team = Team.objects.create(name="team")
        task = Task.objects.create(name="tache")
        response = client.put(
            '/api/maintenancemanagement/addteamtotask', {
                "id_team": f"{team.pk}",
                "id_task": f"{task.pk}"
            },
            format="json"
        )
        self.assertEqual(response.status_code, 201)

    def test_US6_I1_addteamtotask_put_with_perm(self):
        """
            Test if a user without permission can't remove a team from a task.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        team = Team.objects.create(name="team")
        task = Task.objects.create(name="tache")
        response = client.put(
            '/api/maintenancemanagement/addteamtotask', {
                "id_team": f"{team.pk}",
                "id_task": f"{task.pk}"
            },
            format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_US6_I3_teamtaskslist_get_with_perm(self):
        """
            Test if a user with permission can view team's task
        """
        team = Team.objects.create(name="team")
        task = Task.objects.create(name="task")
        task.teams.add(team)
        task.save()
        tasks = team.task_set.all()
        serializer = TaskSerializer(tasks, many=True)
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/maintenancemanagement/teamtasklist/" + str(team.pk), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def test_US6_I3_teamtaskslist_get_without_perm(self):
        """
            Test if a user without permission can't view team's task
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        team = Team.objects.create(name="team")
        task = Task.objects.create(name="task")
        response = client.get(f'/api/maintenancemanagement/teamtasklist/{team.pk}', format='json')
        self.assertEqual(response.status_code, 401)

    def test_US6_I4_usertaskslist_get_with_perm(self):
        """
            Tests if a user with permission can access a user's task list.
        """
        team = Team.objects.create(name="team")
        team2 = Team.objects.create(name="team2")
        task = Task.objects.create(name="task")
        task.teams.add(team)
        task.save()
        user = self.set_up_perm()
        team.user_set.add(user)
        team.save()
        team2.user_set.add(user)
        team2.save()
        tasks = team.task_set.all()
        tasks2 = team2.task_set.all()
        serializer = TaskSerializer(tasks, many=True)
        serializer2 = TaskSerializer(tasks2, many=True)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(f"/api/maintenancemanagement/usertasklist/{user.pk}", format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data + serializer2.data)

    def test_US6_I4_usertaskslist_get_without_perm(self):
        """
            Test if a user without permissions can see his own tasks
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        team = Team.objects.create(name="team")
        team.user_set.add(user)
        team.save()
        task = Task.objects.create(name="task")
        response = client.get(f'/api/maintenancemanagement/usertasklist/{user.pk}', format='json')
        self.assertEqual(response.status_code, 200)

    def test_US8_I1_tasklist_post_with_file_with_perm(self):
        """
            Test if a user with perm can add a task with a file
        """
        user = self.set_up_perm()
        self.add_add_perm_file(user)
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        response1 = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        pk = response1.data['id']
        response = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu',
                'files': [pk]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['files'], [pk])

    def test_US8_I1_tasklist_post_with_file_without_perm(self):
        """
            Test if a user without perm can't add a task with a file
        """
        user = self.set_up_without_perm()
        self.add_add_perm_file(user)
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        response1 = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        pk = response1.data['id']
        response = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu',
                'files': [pk]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_US8_I2_taskdetail_get_with_file_with_perm(self):
        """
            Test if a user with perm can see a task detail with a file
        """
        user = self.set_up_perm()
        self.add_add_perm_file(user)
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        response1 = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        pk_file = response1.data['id']
        response1 = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu',
                'files': [pk_file]
            },
            format='json'
        )
        pk = response1.data['id']
        response = client.get('/api/maintenancemanagement/tasks/' + str(pk) + '/')
        self.assertEqual(response.data['files'], [pk_file])

    def test_US8_I2_taskdetail_get_with_file_withouts_perm(self):
        """
            Test if a user without perm can't see a task detail with a file
        """
        user = self.set_up_perm()
        self.add_add_perm_file(user)
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        response1 = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        pk_file = response1.data['id']
        response1 = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu',
                'files': [pk_file]
            },
            format='json'
        )
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/' + str(pk) + '/')
        self.assertEqual(response.status_code, 401)

    def test_US8_I1_tasklist_post_with_files_with_perm(self):
        """
            Test if a user with perm can add a task with multiple files
        """
        user = self.set_up_perm()
        self.add_add_perm_file(user)
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        data2 = {'file': self.temporary_file(), 'is_manual': 'False'}
        response1 = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        response2 = client.post("/api/maintenancemanagement/files/", data2, format='multipart')
        pk_1 = response1.data['id']
        pk_2 = response2.data['id']
        response = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu',
                'files': [pk_1, pk_2]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['files'], [pk_1, pk_2])

    def test_US8_I1_tasklist_post_with_files_without_perm(self):
        """
            Test if a user without perm can't add a task with multiple files
        """
        user = self.set_up_without_perm()
        self.add_add_perm_file(user)
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        data2 = {'file': self.temporary_file(), 'is_manual': 'False'}
        response1 = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        response2 = client.post("/api/maintenancemanagement/files/", data2, format='multipart')
        pk_1 = response1.data['id']
        pk_2 = response2.data['id']
        response = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu',
                'files': [pk_1, pk_2]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_US8_I2_taskdetail_get_with_files_with_perm(self):
        """
            Test if a user with perm can see a task detail with multiple files
        """
        user = self.set_up_perm()
        self.add_add_perm_file(user)
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        data2 = {'file': self.temporary_file(), 'is_manual': 'False'}
        response1 = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        response2 = client.post("/api/maintenancemanagement/files/", data2, format='multipart')
        pk_1 = response1.data['id']
        pk_2 = response2.data['id']
        response = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu',
                'files': [pk_1, pk_2]
            },
            format='json'
        )
        pk = response.data['id']
        response = client.get('/api/maintenancemanagement/tasks/' + str(pk) + '/')
        self.assertEqual(response.data['files'], [pk_1, pk_2])

    def test_US8_I2_taskdetail_get_with_files_without_perm(self):
        """
            Test if a user without perm can't see a task detail with multiple files
        """
        user = self.set_up_perm()
        self.add_add_perm_file(user)
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        data2 = {'file': self.temporary_file(), 'is_manual': 'False'}
        response1 = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        response2 = client.post("/api/maintenancemanagement/files/", data2, format='multipart')
        pk_1 = response1.data['id']
        pk_2 = response2.data['id']
        response = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name': 'verifier pneus',
                'description': 'faut verfier les pneus de la voiture ta vu',
                'files': [pk_1, pk_2]
            },
            format='json'
        )
        pk = response.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/' + str(pk) + '/')
        self.assertEqual(response.status_code, 401)

    def test_US9_I1_tasklist_post_with_trigger_conditions_with_perm(self):
        """
            Test if a user with perm can add a task with trigger_conditions
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="Trigger Conditions"))
        response = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name':
                    'verifier pneus',
                'description':
                    'desc_task_test_add_task_with_perm_with_trigger_conditions',
                'trigger_conditions':
                    [
                        {
                            "field": conditions.get(name="Date").id,
                            "value": "2020-09-30",
                            "description": "test_add_task_with_perm_with_trigger_conditions_1"
                        },
                        {
                            "field": conditions.get(name="Recurrence").id,
                            "value": "Day",
                            "description": "test_add_task_with_perm_with_trigger_conditions_2"
                        },
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        task = Task.objects.get(description="desc_task_test_add_task_with_perm_with_trigger_conditions")
        field_object_1 = FieldObject.objects.get(description="test_add_task_with_perm_with_trigger_conditions_1")
        field_object_2 = FieldObject.objects.get(description="test_add_task_with_perm_with_trigger_conditions_2")
        self.assertEqual(field_object_1.described_object, task)
        self.assertEqual(field_object_2.described_object, task)

    def test_US11_I1_tasklist_post_with_end_conditions_with_perm(self):
        """
            Test if a user with perm can add a task with end_conditions
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="End Conditions"))
        response = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name':
                    'verifier pneus',
                'description':
                    'desc_task_test_add_task_with_perm_with_end_conditions',
                'end_conditions':
                    [
                        {
                            "field": conditions.get(name="Checkbox").id,
                            "value": "false",
                            "description": "test_add_task_with_perm_with_end_conditions_1"
                        },
                        {
                            "field": conditions.get(name="Integer").id,
                            "value": 0,
                            "description": "test_add_task_with_perm_with_end_conditions_2"
                        },
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        task = Task.objects.get(description="desc_task_test_add_task_with_perm_with_end_conditions")
        field_object_1 = FieldObject.objects.get(description="test_add_task_with_perm_with_end_conditions_1")
        field_object_2 = FieldObject.objects.get(description="test_add_task_with_perm_with_end_conditions_2")
        self.assertEqual(field_object_1.described_object, task)
        self.assertEqual(field_object_2.described_object, task)

    def test_US10_11_I1_tasklist_post_with_end_and_trigger_conditions_with_perm(self):
        """
            Test if a user with perm can add a task with trigger_condition and end_condition
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        trigger_conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="Trigger Conditions"))
        end_conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="End Conditions"))
        response = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name':
                    'verifier pneus',
                'description':
                    'desc_task_test_add_task_with_perm_with_trigger_and_end__conditions',
                'trigger_conditions':
                    [
                        {
                            "field": trigger_conditions.get(name="Recurrence").id,
                            "value": "Month",
                            "description": "test_add_task_with_perm_with_trigger_and_end_conditions_1"
                        }
                    ],
                'end_conditions':
                    [
                        {
                            "field": end_conditions.get(name="Checkbox").id,
                            "value": "false",
                            "description": "test_add_task_with_perm_with_trigger_and_end_conditions_2"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        task = Task.objects.get(description="desc_task_test_add_task_with_perm_with_trigger_and_end__conditions")
        field_object_1 = FieldObject.objects.get(
            description="test_add_task_with_perm_with_trigger_and_end_conditions_1"
        )
        field_object_2 = FieldObject.objects.get(
            description="test_add_task_with_perm_with_trigger_and_end_conditions_2"
        )
        self.assertEqual(field_object_1.described_object, task)
        self.assertEqual(field_object_2.described_object, task)
        self.assertEqual(field_object_1.field_value, FieldValue.objects.get(value='Month'))

    def test_US10_11_I1_tasklist_post_with_conditions_with_bad_values_with_perm(self):
        """
            Test if a user with perm can add a task with conditons with bad values
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="Trigger Conditions"))
        response = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name':
                    'verifier pneus',
                'description':
                    'desc_task_test_add_task_with_perm_with_conditions_with_bad_values',
                'trigger_conditions':
                    [
                        {
                            "field": conditions.get(name="Recurrence").id,
                            "value": "BAD_VALUE",
                            "description": "test_add_task_with_perm_with_conditions_with_bad_values"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_US19_I1_taskrequirements_with_perm(self):
        """
            Test if a user can get template requirements with permission
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/requirements')
        trigger_conditions = response.data['trigger_conditions']
        end_conditions = response.data['end_conditions']
        template = Task.objects.get(name='TemplateTest')
        template_json = {
            'id': template.id,
            'name': template.name,
            'end_date': template.end_date,
            'description': template.description,
            'duration': '2 00:00:00',
            'is_template': template.is_template,
            'equipment': template.equipment,
            'files': list(template.files.all()),
            'teams': list(template.teams.all().values_list('id', flat=True)),
            'equipment_type':
                {
                    'id': template.equipment_type.id,
                    'name': template.equipment_type.name,
                    'fields_groups': list(template.equipment_type.fields_groups.all().values_list('id', flat=True)),
                    'equipment_set': list(template.equipment_type.equipment_set.all().values_list('id', flat=True)),
                },
            'over': template.over,
            'trigger_conditions': [],
            'end_conditions': []
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(trigger_conditions),
            len(Field.objects.filter(field_group=FieldGroup.objects.get(name="Trigger Conditions")))
        )
        self.assertEqual(
            len(end_conditions), len(Field.objects.filter(field_group=FieldGroup.objects.get(name="End Conditions")))
        )
        self.assertTrue(template_json in response.json().get('task_templates'))

    def test_US19_I1_taskrequirements_without_perm(self):
        """
            Test if a user can get template requirements without permission
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/requirements')
        self.assertEqual(response.status_code, 401)
