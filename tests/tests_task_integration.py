from datetime import timedelta
from io import BytesIO

import pytest
from init_db_tests import init_db
from PIL import Image

from django.contrib.auth.models import Permission
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

    def temporary_file(self):
        """
        Returns a new temporary image.
        """
        file_obj = BytesIO()
        image = Image.new('1', (60, 60), 1)
        image.save(file_obj, 'png')
        file_obj.seek(0)
        return file_obj

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

    def test_US5_I1_tasklist_get_only_templates_with_perm(self):
        """
            Test if a user with perm receive the data
        """
        user = self.set_up_perm()
        tasks = Task.objects.filter(is_template=True)
        serializer = TaskListingSerializer(tasks, many=True)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/', {"template": "true"}, format='json')
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

    def test_US5_I3_taskdetail_get_non_existing_task_with_perm(self):
        """
            Test if a user with perm can't see an unavailable task detail
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
        response = client.get('/api/maintenancemanagement/tasks/' + str(10506466) + '/')
        self.assertEqual(response.status_code, 404)

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

    def test_US5_I4_taskdetail_put_non_existing_task_with_perm(self):
        """
            Test if a user with perm can't change an unavailable task
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
            '/api/maintenancemanagement/tasks/' + str(644687456) + '/', {'name': 'verifier roues'}, format='json'
        )
        self.assertEqual(response.status_code, 404)

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

    def test_US5_I4_taskdetail_put_with_end_condition_with_perm(self):
        """
            Test if a user with perm can change a task
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        conditions = Field.objects.filter(field_group=FieldGroup.objects.get(name="End Conditions"))
        checkbox = conditions.get(name="Checkbox")
        entier = conditions.get(name="Integer")
        response1 = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name':
                    'verifier pneus',
                'description':
                    'faut verfier les pneus de la voiture ta vu',
                'end_conditions':
                    [
                        {
                            "field": checkbox.id,
                            "value": "false",
                            "description": "test_update_task_with_perm_with_end_conditions_1"
                        },
                        {
                            "field": entier.id,
                            "value": 0,
                            "description": "test_update_task_with_perm_with_end_conditions_2"
                        },
                    ]
            },
            format='json'
        )
        pk = response1.data['id']
        response = client.put(
            '/api/maintenancemanagement/tasks/' + str(pk) + '/', {
                'name':
                    'verifier roues',
                'duration':
                    '30d',
                'end_conditions':
                    [
                        {
                            "field": FieldObject.objects.get(field=checkbox).id,
                            "value": "false",
                            "description": "maj_checkbox"
                        },
                        {
                            "field": FieldObject.objects.get(field=entier).id,
                            "value": 10,
                            "description": "maj_entier"
                        },
                    ]
            },
            format='json'
        )
        self.assertEqual(response.data['name'], 'verifier roues')
        self.assertEqual(response.status_code, 200)

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

    def test_US5_I5_taskdetail_delete_non_existing_task_with_perm(self):
        """
            Test if a user with perm can't delete an unavailable task
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.delete('/api/maintenancemanagement/tasks/' + str(6546546) + '/')
        self.assertEqual(response.status_code, 404)

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
            '/api/maintenancemanagement/addteamtotask', {
                "id_team": f"{team.pk}",
                "id_task": f"{task.pk}"
            },
            format="json"
        )
        self.assertEqual(response.status_code, 201)

    def test_US6_I1_addteamtotask_post_without_perm(self):
        """
            Test if a user without permission can't add a team to a task.
        """
        user = self.set_up_perm()
        user.user_permissions.clear()
        client = APIClient()
        client.force_authenticate(user=user)
        team = Team.objects.create(name="team")
        task = Task.objects.create(name="tache")
        response = client.post(
            '/api/maintenancemanagement/addteamtotask', {
                "id_team": f"{team.pk}",
                "id_task": f"{task.pk}"
            },
            format="json"
        )
        self.assertEqual(response.status_code, 401)

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

    def test_US6_I3_teamtaskslist_get_non_existing_team_with_perm(self):
        """
            Test if a user with permission can't view non existing team's task
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/maintenancemanagement/teamtasklist/" + str(65465464), format='json')
        self.assertEqual(response.status_code, 404)

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
        serializer = TaskListingSerializer(tasks, many=True)
        serializer2 = TaskListingSerializer(tasks2, many=True)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(f"/api/maintenancemanagement/usertasklist/{user.pk}", format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data + serializer2.data)

    def test_US6_I4_usertaskslist_get_non_existing_user_with_perm(self):
        """
            Tests if a user with permission can't access a non existing user's task list.
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(f"/api/maintenancemanagement/usertasklist/{6546874}", format='json')
        self.assertEqual(response.status_code, 404)

    def test_US6_I4_usertaskslist_get_without_perm(self):
        """
            Test if a user without permissions can see his own tasks
        """
        temp_user = self.set_up_perm()
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        team = Team.objects.create(name="team")
        team.user_set.add(user)
        team.save()
        response = client.get(f'/api/maintenancemanagement/usertasklist/{temp_user.pk}', format='json')
        self.assertEqual(response.status_code, 401)

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
        files = File.objects.filter(pk=pk_file)
        self.assertEqual(response.data['files'], FileSerializer(files, many=True).data)

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
        files = File.objects.filter(pk__in=[pk_1, pk_2])
        self.assertEqual(response.data['files'], FileSerializer(files, many=True).data)

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
        field_object = FieldObject.objects.get(field=Field.objects.get(name="Nb bouteilles"))
        nb_bouteilles_value = float(field_object.value)
        response = client.post(
            '/api/maintenancemanagement/tasks/', {
                'name':
                    'verifier pneus',
                'description':
                    'desc_task_test_add_task_with_perm_with_trigger_conditions',
                'trigger_conditions':
                    [
                        {
                            "field": conditions.get(name="Recurrence").id,
                            "value": "30d",
                            "delay": "7d",
                            "description": "test_add_task_with_perm_with_trigger_conditions_recurrence"
                        }, {
                            'field': conditions.get(name='Above Threshold').id,
                            'value': '0.6',
                            'field_object_id': field_object.id,
                            'delay': '2d',
                            'description': 'test_add_task_with_perm_with_trigger_conditions_above_threshold'
                        }, {
                            'field': conditions.get(name='Under Threshold').id,
                            'value': '0.6',
                            'field_object_id': field_object.id,
                            'delay': '2d',
                            'description': 'test_add_task_with_perm_with_trigger_conditions_under_threshold'
                        }, {
                            'field': conditions.get(name='Frequency').id,
                            'value': '10000',
                            'field_object_id': field_object.id,
                            'delay': '2d',
                            'description': 'test_add_task_with_perm_with_trigger_conditions_frequency'
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        task = Task.objects.get(description="desc_task_test_add_task_with_perm_with_trigger_conditions")
        self.assertFalse(task.is_triggered)
        field_object1 = FieldObject.objects.get(
            description="test_add_task_with_perm_with_trigger_conditions_recurrence"
        )
        field_object2 = FieldObject.objects.get(
            description="test_add_task_with_perm_with_trigger_conditions_above_threshold"
        )
        field_object3 = FieldObject.objects.get(
            description="test_add_task_with_perm_with_trigger_conditions_under_threshold"
        )
        field_object4 = FieldObject.objects.get(
            description="test_add_task_with_perm_with_trigger_conditions_frequency"
        )
        self.assertEqual(field_object1.described_object, task)
        self.assertEqual(field_object1.value, '30d|7d')
        self.assertEqual(field_object2.value, f'0.6|{field_object.id}|2d')
        self.assertEqual(field_object3.value, f'0.6|{field_object.id}|2d')
        self.assertEqual(field_object4.value, f'10000|{field_object.id}|2d|{nb_bouteilles_value + 10000}')

    def test_US9_I1_tasklist_post_with_trigger_conditions_with_perm_and_wrong_values_1(self):
        """
            Test if a user with perm can't add a task with trigger_conditions with bad values.
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
                            "field": conditions.get(name="Recurrence").id,
                            "value": "30d",
                            "description": "test_add_task_with_perm_with_trigger_conditions_recurrence"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_US9_I1_tasklist_post_with_trigger_conditions_with_perm_and_wrong_values_2(self):
        """
            Test if a user with perm can't add a task with trigger_conditions with bad values.
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
                            "field": conditions.get(name="Recurrence").id,
                            "value": "30d",
                            'delay': '2d',
                            "description": "test_add_task_with_perm_with_trigger_conditions_recurrence",
                            'field_object_id': 1,
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_US9_I1_tasklist_post_with_trigger_conditions_with_perm_and_wrong_values_3(self):
        """
            Test if a user with perm can't add a task with trigger_conditions with bad values.
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
                            'field': conditions.get(name='Above Threshold').id,
                            'value': '0.6',
                            'field_object_id': 1,
                            'description': 'test_add_task_with_perm_with_trigger_conditions_above_threshold'
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_US9_I1_tasklist_post_with_trigger_conditions_with_perm_and_wrong_values_4(self):
        """
            Test if a user with perm can't add a task with trigger_conditions with bad values.
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
                            'field': conditions.get(name='Above Threshold').id,
                            'value': '0.6',
                            'delay': '2d',
                            'description': 'test_add_task_with_perm_with_trigger_conditions_above_threshold'
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

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
        self.assertTrue(task.is_triggered)
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
            '/api/maintenancemanagement/tasks/',
            {
                'name':
                    'verifier pneus',
                'description':
                    'desc_task_test_add_task_with_perm_with_trigger_and_end__conditions',
                'trigger_conditions':
                    [
                        {
                            "field": trigger_conditions.get(name="Recurrence").id,
                            # "field_object_id": 2,  # Si on le met pas ça dit qu'il est requis, si on le mets ça plante
                            "value": "30d",
                            "delay": "14d",
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
            'duration': '2d',
            'is_template': template.is_template,
            'equipment': None,
            'files': FileSerializer(template.files.all(), many=True).data,
            'teams': TeamSerializer(template.teams.all(), many=True).data,
            'equipment_type': EquipmentTypeSerializer(template.equipment_type).data,
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
