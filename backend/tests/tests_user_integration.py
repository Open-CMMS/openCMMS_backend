from django.urls import reverse
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.contrib.auth.models import Permission
from usersmanagement.models import UserProfile, Team, TeamType
from rest_framework.test import APIClient
from usersmanagement.views.views_user import *
from django.contrib.contenttypes.models import ContentType
from usersmanagement.views.views_user import is_first_user, init_database

class UserTests(TestCase):

    def set_up_perm(self):
        """
            Set up a user with permissions
        """
        content_type = ContentType.objects.get_for_model(UserProfile)
        permission = Permission.objects.create(codename='add_UserProfile',
                                       name='Can add a user',
                                       content_type=content_type)
        permission2 = Permission.objects.create(codename='view_UserProfile',
                                       name='Can view a user',
                                       content_type=content_type)  
        permission3 = Permission.objects.create(codename='delete_UserProfile',
                                       name='Can delete a user',
                                       content_type=content_type)
        permission4 = Permission.objects.create(codename='change_UserProfile',
                                       name='Can update a user',
                                       content_type=content_type)                             
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

    def test_can_acces_users_list_with_perm(self):
        """
            Test if a user with perm receive the data
        """
        user = self.set_up_perm()
        users = UserProfile.objects.all()
        serializer = UserProfileSerializer(users, many=True)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/usersmanagement/users/', format='json')
        self.assertEqual(response.data,serializer.data)

    def test_can_acces_users_list_without_perm(self):
        """
            Test if a user without perm doesn't receive the data
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/usersmanagement/users/', format='json')
        self.assertEqual(response.status_code,401)

    def test_add_user_first_user(self):
        """
            Test if a user without perm and is first user can add a user
        """
        client = APIClient()
        client.login(username='tom', password='truc')
        response = client.post('/api/usersmanagement/users/', {'username': 'joey', 'password' : 'machin'}, format='json')
        self.assertEqual(response.status_code,201)

    def test_add_user_with_perm(self):
        """
            Test if a user with perm and is not first user can add a user
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/usersmanagement/users/', {'username': 'joey', 'password' : 'machin'}, format='json')
        self.assertEqual(response.status_code,201)

    def test_add_user_without_perm(self):
        """
            Test if a user without perm can't add a user
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/usersmanagement/users/', {'username': 'joey', 'password' : 'machin'}, format='json')
        self.assertEqual(response.status_code,401)

    def test_is_first_user_with_first_user_request(self):
        """
            Test is_first_user with the first user
        """
        client = APIClient()
        UserProfile.objects.all().delete()
        request = client.get('/api/usersmanagement/users/is_first_user', format='json')
        self.assertEqual(request.data,True)

    def test_is_first_user_without_first_user_request(self):
        """
            Test is_first_user without the first user
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        request = client.get('/api/usersmanagement/users/is_first_user', format='json')
        self.assertEqual(request.data,False)


    def test_username_suffix_with_existant(self):
        """
            Test that the fonction give the correct number to put after an username
        """
        user = self.set_up_perm()
        c = Client()
        response = c.get('/api/usersmanagement/users/username_suffix?username=tom')
        self.assertEqual(response.data, '1')

    def test_username_suffix_without_existant(self):
        """
            Test that the fonction give empty string to put after an username
        """
        c = Client()
        response = c.get('/api/usersmanagement/users/username_suffix?username=yolo')
        self.assertEqual(response.data, "")


    def test_view_user_request_own_detail(self):
        """
            Test if a user without perm can see his own detail
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/usersmanagement/users/'+str(user.pk)+'/')
        self.assertEqual(response.data['username'],'tom')


    def test_view_user_request_with_perm(self):
        """
            Test if a user with perm can see another user detail
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/usersmanagement/users/', {'username': 'joey', 'password' : 'machin'}, format='json')
        pk = response1.data['id']
        response = client.get('/api/usersmanagement/users/'+str(pk)+'/')
        self.assertEqual(response.data['username'],'joey')

    def test_view_user_request_without_perm(self):
        """
            Test if a user without perm can see another user detail
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/usersmanagement/users/', {'username': 'joey', 'password' : 'machin'}, format='json')
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.get('/api/usersmanagement/users/'+str(pk)+'/')
        self.assertEqual(response.status_code,401)


    def test_change_user_request_own_detail(self):
        """
            Test if a user can change his own detail
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.put('/api/usersmanagement/users/'+str(user.pk)+'/', {'first_name':'Paul'}, format='json')
        self.assertEqual(response.data['first_name'],'Paul')


    def test_change_user_request_with_perm(self):
        """
            Test if a user with perm can change another user detail
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/usersmanagement/users/', {'username': 'joey', 'password' : 'machin', 'first_name' : 'Joey'}, format='json')
        pk = response1.data['id']
        response = client.put('/api/usersmanagement/users/'+str(pk)+'/', {'first_name':'Paul'}, format='json')
        self.assertEqual(response.data['first_name'],'Paul')

    def test_change_user_request_without_perm(self):
        """
            Test if a user without perm can change another user detail
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/usersmanagement/users/', {'username': 'joey', 'password' : 'machin', 'first_name' : 'Joey'}, format='json')
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.put('/api/usersmanagement/users/'+str(pk)+'/', {'first_name':'Paul'}, format='json')
        self.assertEqual(response.status_code,401)


    def test_delete_user_request_with_perm(self):
        """
            Test if a user with perm can delete another user
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/usersmanagement/users/', {'username': 'joey', 'password' : 'machin', 'first_name' : 'Joey'}, format='json')
        pk = response1.data['id']
        response = client.delete('/api/usersmanagement/users/'+str(pk)+'/')
        self.assertEqual(response.status_code, 204)

    def test_delete_user_request_without_perm(self):
        """
            Test if a user without perm can delete another user
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post('/api/usersmanagement/users/', {'username': 'joey', 'password' : 'machin', 'first_name' : 'Joey'}, format='json')
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.delete('/api/usersmanagement/users/'+str(pk)+'/')
        self.assertEqual(response.status_code,401)


    def test_init_database(self):
        """
            Test the good function of init_database
        """
        users = UserProfile.objects.all()
        users.delete()
        teams = Team.objects.all()
        teams.delete()
        teamtypes = TeamType.objects.all()
        teamtypes.delete()

        user = self.set_up_without_perm()

        init_database()

        self.assertEqual(user.groups.all().count(), 1)
        self.assertEqual(Team.objects.all().count(), 3)
        self.assertEqual(TeamType.objects.all().count(), 3)
        self.assertEqual('usersmanagement.add_userprofile' in user.get_all_permissions(), True)
