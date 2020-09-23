from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from maintenancemanagement.models import Task, TaskType
from maintenancemanagement.serializers import TaskTypeSerializer
from rest_framework.test import APIClient
from usersmanagement.models import UserProfile


class TaskTypeTests(TestCase):

    def set_up_perm(self):
        """
            Set up a user with permissions
        """
        permission = Permission.objects.get(codename='add_tasktype')
        permission2 = Permission.objects.get(codename='view_tasktype')
        permission3 = Permission.objects.get(codename='delete_tasktype')
        permission4 = Permission.objects.get(codename='change_tasktype')

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

    def test_can_acces_task_type_list_with_perm(self):
        """
            Test if a user with perm receive the data of tasktype
        """
        user = self.set_up_perm()
        tasktypes = TaskType.objects.all()
        serializer = TaskTypeSerializer(tasktypes, many=True)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasktypes/', format='json')
        self.assertEqual(response.data, serializer.data)

    def test_can_acces_task_type_list_without_perm(self):
        """
            Test if a user without perm doesn't receive the data of tasktype
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasktypes/', format='json')
        self.assertEqual(response.status_code, 401)

    def test_add_tasktype_with_perm(self):
        """
            Test if a user with perm can add a tasktype
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/maintenancemanagement/tasktypes/', {'name': 'Maintenance Voiture'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Maintenance Voiture')

    def test_add_tasktype_without_perm(self):
        """
            Test if a user without perm can't add a tasktype
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/maintenancemanagement/tasktypes/', {'name': 'Maintenance Voiture'}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_view_tasktype_with_perm(self):
        """
            Test if a user with perm can see a tasktype detail
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/maintenancemanagement/tasktypes/', {'name': 'Maintenance Voiture'}, format='json'
        )
        pk = response1.data['id']
        response = client.get('/api/maintenancemanagement/tasktypes/' + str(pk) + '/')
        self.assertEqual(response.data['name'], 'Maintenance Voiture')

    def test_view_tasktype_without_perm(self):
        """
            Test if a user without perm can't see a tasktype detail
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/maintenancemanagement/tasktypes/', {'name': 'Maintenance Voiture'}, format='json'
        )
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasktypes/' + str(pk) + '/')
        self.assertEqual(response.status_code, 401)

    def test_change_tasktype_with_perm(self):
        """
            Test if a user with perm can change a tasktype
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/maintenancemanagement/tasktypes/', {'name': 'Maintenance Voiture'}, format='json'
        )
        pk = response1.data['id']
        response = client.put(
            '/api/maintenancemanagement/tasktypes/' + str(pk) + '/', {'name': 'Maintenance Tuture'}, format='json'
        )
        self.assertEqual(response.data['name'], 'Maintenance Tuture')
        self.assertEqual(response.status_code, 200)

    def test_change_tasktype_without_perm(self):
        """
            Test if a user without perm can change a task
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/maintenancemanagement/tasktypes/', {'name': 'Maintenance Voiture'}, format='json'
        )
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.put(
            '/api/maintenancemanagement/tasktypes/' + str(pk) + '/', {'name': 'Maintenance Tuture'}, format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_tasktype_with_perm(self):
        """
            Test if a user with perm can delete a tasktype
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/maintenancemanagement/tasktypes/', {'name': 'Maintenance Voiture'}, format='json'
        )
        pk = response1.data['id']
        response = client.delete('/api/maintenancemanagement/tasktypes/' + str(pk) + '/')
        self.assertEqual(response.status_code, 204)

    def test_delete_tasktype_without_perm(self):
        """
            Test if a user without perm can delete a tasktype
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/maintenancemanagement/tasktypes/', {'name': 'Maintenance Voiture'}, format='json'
        )
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.delete('/api/maintenancemanagement/tasktypes/' + str(pk) + '/')
        self.assertEqual(response.status_code, 401)
