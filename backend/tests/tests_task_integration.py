from django.test import TestCase, Client
from maintenancemanagement.models import Task, TaskType
from maintenancemanagement.serializers import TaskSerializer
from usersmanagement.models import Team
from rest_framework.test import APIClient
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from usersmanagement.models import UserProfile
from openCMMS import settings
from datetime import timedelta

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
        response = client.put('/api/maintenancemanagement/tasks/'+str(pk)+'/', {'name':'verifier roues'}, format='json')
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
        response = client.put('/api/maintenancemanagement/tasks/'+str(pk)+'/', {'name':'verifier roues'}, format='json')
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

    def test_can_acces_task_list_with_perm_with_end_date(self):
        """
            Test if a user with perm receive the data with end_date
        """
        user = self.set_up_perm()
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/', format='json')
        self.assertEqual(response.data,serializer.data)

    def test_can_acces_task_list_without_perm_with_end_date(self):
        """
            Test if a user without perm doesn't receive the data with end_date
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/', format='json')
        self.assertEqual(response.status_code,401)

    def test_add_task_with_perm_with_end_date(self):
        """
            Test if a user with perm can add a task with end_date
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu', 'end_date': '2020-04-29'}, format='json')
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.data['end_date'], '2020-04-29')

    def test_add_task_without_perm_with_end_date(self):
        """
            Test if a user without perm can't add a task with end_date
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu', 'end_date': '2020-04-29'}, format='json')
        self.assertEqual(response.status_code,401)

    def test_view_task_request_with_perm_with_end_date(self):
        """
            Test if a user with perm can see a task detail with end_date
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu','end_date': '2020-04-29'}, format='json')
        pk = response1.data['id']
        response = client.get('/api/maintenancemanagement/tasks/'+str(pk)+'/')
        self.assertEqual(response.data['end_date'],'2020-04-29')

    def test_view_task_request_without_perm_with_end_date(self):
        """
            Test if a user without perm can't see a task detail with end_date
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu','end_date': '2020-04-29'}, format='json')
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/'+str(pk)+'/')
        self.assertEqual(response.status_code,401)

    def test_change_task_with_perm_with_end_date(self):
        """
            Test if a user with perm can change a task with end_date
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu','end_date': '2020-04-29'}, format='json')
        pk = response1.data['id']
        response = client.put('/api/maintenancemanagement/tasks/'+str(pk)+'/', {'end_date':'2020-03-12'}, format='json')
        self.assertEqual(response.data['end_date'],'2020-03-12')
        self.assertEqual(response.status_code, 200)


    def test_change_task_without_perm_with_end_date(self):
        """
            Test if a user without perm can change a task with end_date
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu','end_date': '2020-04-29'}, format='json')
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.put('/api/maintenancemanagement/tasks/'+str(pk)+'/', {'end_date':'2020-03-12'}, format='json')
        self.assertEqual(response.status_code, 401)


    def test_delete_task_with_perm_with_end_date(self):
        """
            Test if a user with perm can delete a task with end_date
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu','end_date': '2020-04-29'}, format='json')
        pk = response1.data['id']
        response = client.delete('/api/maintenancemanagement/tasks/'+str(pk)+'/')
        self.assertEqual(response.status_code, 204)


    def test_delete_task_without_perm_with_end_date(self):
        """
            Test if a user without perm can delete a task with end_date
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu','end_date': '2020-04-29'}, format='json')
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.delete('/api/maintenancemanagement/tasks/'+str(pk)+'/')
        self.assertEqual(response.status_code,401)

    def test_can_acces_task_list_with_perm_with_time(self):
        """
            Test if a user with perm receive the data with end_date
        """
        user = self.set_up_perm()
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/', format='json')
        self.assertEqual(response.data,serializer.data)

    def test_can_acces_task_list_without_perm_with_time(self):
        """
            Test if a user without perm doesn't receive the data with time
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/', format='json')
        self.assertEqual(response.status_code,401)

    def test_add_task_with_perm_with_time(self):
        """
            Test if a user with perm can add a task with time
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu', 'time': '1 day, 8:00:00'}, format='json')
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.data['time'], '1 08:00:00')

    def test_add_task_without_perm_with_time(self):
        """
            Test if a user without perm can't add a task with time
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu', 'time': timedelta(days=1, hours=8)}, format='json')
        self.assertEqual(response.status_code,401)

    def test_view_task_request_with_perm_with_time(self):
        """
            Test if a user with perm can see a task detail with time
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu','time': timedelta(days=1, hours=8)}, format='json')
        pk = response1.data['id']
        response = client.get('/api/maintenancemanagement/tasks/'+str(pk)+'/')
        self.assertEqual(response.data['time'],'1 08:00:00')

    def test_view_task_request_without_perm_with_time(self):
        """
            Test if a user without perm can't see a task detail with time
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu','time': timedelta(days=1, hours=8)}, format='json')
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/tasks/'+str(pk)+'/')
        self.assertEqual(response.status_code,401)

    def test_change_task_with_perm_with_time(self):
        """
            Test if a user with perm can change a task with time
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu','time': timedelta(days=1, hours=8)}, format='json')
        pk = response1.data['id']
        response = client.put('/api/maintenancemanagement/tasks/'+str(pk)+'/', {'time': timedelta(days=2, hours=4)}, format='json')
        self.assertEqual(response.data['time'],'2 04:00:00')
        self.assertEqual(response.status_code, 200)


    def test_change_task_without_perm_with_time(self):
        """
            Test if a user without perm can change a task with time
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu','time': timedelta(days=1, hours=8)}, format='json')
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.put('/api/maintenancemanagement/tasks/'+str(pk)+'/', {'time': timedelta(days=2, hours=4)}, format='json')
        self.assertEqual(response.status_code, 401)


    def test_delete_task_with_perm_with_time(self):
        """
            Test if a user with perm can delete a task with time
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu','time': timedelta(days=1, hours=8)}, format='json')
        pk = response1.data['id']
        response = client.delete('/api/maintenancemanagement/tasks/'+str(pk)+'/')
        self.assertEqual(response.status_code, 204)


    def test_delete_task_without_perm_with_time(self):
        """
            Test if a user without perm can delete a task with time
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/maintenancemanagement/tasks/', {'name': 'verifier pneus', 'description' : 'faut verfier les pneus de la voiture ta vu','time': timedelta(days=1, hours=8)}, format='json')
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.delete('/api/maintenancemanagement/tasks/'+str(pk)+'/')
        self.assertEqual(response.status_code,401)
    
    def test_add_team_task_with_authorization(self):
        """
            Test if a user with permission can add a team to a task.
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        team = Team.objects.create(name="team")
        task = Task.objects.create(name="tache")
        response = client.post('/api/maintenancemanagement/add_team_to_task/', {"id_team": f"{team.pk}", "id_task": f"{task.pk}" }, format="json")
        self.assertEqual(response.status_code, 201)

    def test_add_team_task_with_authorization(self):
        """
            Test if a user with permission can remove a team from a task.
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        team = Team.objects.create(name="team")
        task = Task.objects.create(name="tache")
        response = client.put('/api/maintenancemanagement/addteamtotask', {"id_team": f"{team.pk}", "id_task": f"{task.pk}" }, format="json")
        self.assertEqual(response.status_code, 201)

    def test_add_team_task_without_authorization(self):
        """
            Test if a user without permission can't remove a team from a task.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        team = Team.objects.create(name="team")
        task = Task.objects.create(name="tache")
        response = client.put('/api/maintenancemanagement/addteamtotask', {"id_team": f"{team.pk}", "id_task": f"{task.pk}" }, format="json")
        self.assertEqual(response.status_code, 401)

    def test_view_team_s_tasks_with_auth(self):
        team = Team.objects.create(name="team")
        task = Task.objects.create(name="task")
        task.teams.add(team)
        task.save()
        tasks = team.task_set.all()
        serializer = TaskSerializer(tasks, many=True)
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/maintenancemanagement/teamtasklist/"+str(team.pk), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)
    
    def test_view_team_s_tasks_without_auth(self):
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        team = Team.objects.create(name="team")
        task = Task.objects.create(name="task")
        response = client.get(f'/api/maintenancemanagement/teamtasklist/{team.pk}', format='json')
        self.assertEqual(response.status_code, 401)
    
    def test_view_team_s_tasks_with_auth(self):
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
        self.assertEqual(response.data, serializer.data+serializer2.data)
    
    def test_view_team_s_tasks_without_auth(self):
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        team = Team.objects.create(name="team")
        team.user_set.add(user)
        team.save()
        task = Task.objects.create(name="task")
        response = client.get(f'/api/maintenancemanagement/usertasklist/{user.pk}', format='json')
        self.assertEqual(response.status_code, 401)