from django.test import TestCase, Client
from maintenancemanagement.models import Task, TaskType
from maintenancemanagement.serializers import TaskSerializer
from rest_framework.test import APIClient
from django.contrib.contenttypes.models import ContentType



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
        user.first_name='Tom'
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
        user.first_name='Tom'
        user.save()
        return user


    def test_can_acces_task_list_with_perm(self):
        """
            Test if a user with perm receive the data
        """
        user = self.set_up_perm()
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/', format='json')
        self.assertEqual(response.data,serializer.data)

    def test_can_acces_task_list_without_perm(self):
        """
            Test if a user without perm doesn't receive the data
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/', format='json')
        self.assertEqual(response.status_code,401)

    def test_add_task_with_perm(self):
        """
            Test if a user with perm can add a task
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu'}, format='json')
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.data['name'], 'verifier pneus')

    def test_add_task_without_perm(self):
        """
            Test if a user without perm can't add a task
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu'}, format='json')
        self.assertEqual(response.status_code,401)

    def test_view_task_request_with_perm(self):
        """
            Test if a user with perm can see a task detail
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu'}, format='json')
        pk = response1.data['id']
        response = client.get('/api/maintenancemanagement/tasks/'+str(pk)+'/')
        self.assertEqual(response.data['name'],'verifier pneus')

    def test_view_task_request_without_perm(self):
        """
            Test if a user without perm can't see a task detail
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu'}, format='json')
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/'+str(pk)+'/')
        self.assertEqual(response.status_code,401)

    def test_change_task_with_perm(self):
        """
            Test if a user with perm can change a task
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu'}, format='json')
        pk = response1.data['id']
        response = client.put('/api/maintenancemanagement/tasks/'+str(user.pk)+'/', {'name':'verifier roues'}, format='json')
        self.assertEqual(response.data['name'],'verifier roues')
        self.assertEqual(response.status_code, 200)


    def test_change_task_without_perm(self):
        """
            Test if a user without perm can change a task
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu'}, format='json')
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.put('/api/maintenancemanagement/tasks/'+str(user.pk)+'/', {'name':'verifier roues'}, format='json')
        self.assertEqual(response.status_code, 401)


    def test_delete_task_with_perm(self):
        """
            Test if a user with perm can delete a task
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu'}, format='json')
        pk = response1.data['id']
        response = client.delete('/api/maintenancemanagement/tasks/'+str(pk)+'/')
        self.assertEqual(response.status_code, 204)


    def test_delete_task_without_perm(self):
        """
            Test if a user without perm can delete a task
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu'}, format='json')
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.delete('/api/maintenancemanagement/tasks/'+str(pk)+'/')
        self.assertEqual(response.status_code,401)