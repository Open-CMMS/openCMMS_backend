from django.urls import reverse
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import Permission
from usersmanagement.models import UserProfile
from rest_framework.test import APIClient
from usersmanagement.views.views_user import *
from django.contrib.contenttypes.models import ContentType

class UserTests(TestCase):

    def set_up_perm(self):
        """
            Set up a user with permissions
        """
        content_type = ContentType.objects.get_for_model(UserProfile)
        permission = Permission.objects.create(codename='add_UserProfile',
                                       name='Can add a user',
                                       content_type=content_type)
        user = UserProfile(username='tom')
        user.set_password('truc')
        user.save()
        user.user_permissions.add(permission)
        user.save()
        return user

    def set_up_without_perm(self):
        """
            Set up a user without permissions
        """
        user = UserProfile(username='tom')
        user.set_password('truc')
        user.save()
        return user

    def test_can_acces_users_list_with_perm(self):
        """
            Test if a user with perm receive the data
        """
        self.set_up_perm()
        users = UserProfile.objects.all()
        serializer = UserProfileSerializer(users, many=True)
        client = APIClient()
        client.login(username='tom', password='truc')
        response = client.get('/api/gestion/users/', format='json')
        self.assertEqual(response.data,serializer.data)

    def test_can_acces_users_list_without_perm(self):
        """
            Test if a user without perm doesn't receive the data
        """
        self.set_up_without_perm()
        client = APIClient()
        client.login(username='tom', password='truc')
        response = client.get('/api/gestion/users/', format='json')
        self.assertEqual(response.status_code,401)

    def test_add_user_first_user(self):
        """
            Test if a user without perm and is first user can add a user
        """
        client = APIClient()
        client.login(username='tom', password='truc')
        response = client.post('/api/gestion/users/', {'username': 'joey', 'password' : 'machin'}, format='json')
        self.assertEqual(response.status_code,201)

    def test_add_user_with_perm(self):
        """
            Test if a user with perm and is not first user can add a user
        """
        self.set_up_perm()
        client = APIClient()
        client.login(username='tom', password='truc')
        response = client.post('/api/gestion/users/', {'username': 'joey', 'password' : 'machin'}, format='json')
        self.assertEqual(response.status_code,201)

    def test_add_user_without_perm(self):
        """
            Test if a user without perm can't add a user
        """
        self.set_up_without_perm()
        user = UserProfile(username='bob')
        user.set_password('buh')
        user.save()
        client = APIClient()
        client.login(username='bob', password='buh')
        response = client.post('/api/gestion/users/', {'username': 'joey', 'password' : 'machin'}, format='json')
        self.assertEqual(response.status_code,401)

    def test_is_first_user_with_first_user_request(self):
        """
            Test is_first_user with the first user
        """
        client = APIClient()
        client.login(username='tom', password='truc')
        request = client.get('/api/gestion/users/is_first_user', format='json')
        self.assertEqual(request.data,True)

    def test_is_first_user_without_first_user_request(self):
        """
            Test is_first_user without the first user
        """
        self.set_up_without_perm()
        client = APIClient()
        client.login(username='joe', password='machin')
        request = client.get('/api/gestion/users/is_first_user', format='json')
        self.assertEqual(request.data,False)
