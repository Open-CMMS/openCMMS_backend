from usersmanagement.models import Team, TeamType, UserProfile
from usersmanagement.views.views_user import *
from usersmanagement.views.views_user import init_database, is_first_user

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class UserTests(TestCase):

    def set_up_perm(self):
        """
            Set up a user with permissions
        """
        content_type = ContentType.objects.get_for_model(UserProfile)
        permission = Permission.objects.get(codename='add_userprofile')
        permission2 = Permission.objects.get(codename='view_userprofile')
        permission3 = Permission.objects.get(codename='delete_userprofile')
        permission4 = Permission.objects.get(codename='change_userprofile')
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

    def test_US2_I1_userlist_get_with_perm(self):
        """
            Test if a user with permission can view the users' list.

            Inputs:
                serializer (UserProfileSerializer): a serializer containing all users data.

            Expected Output:
                We expect to get in the response the same data as in serializer.
        """
        user = self.set_up_perm()
        users = UserProfile.objects.all()
        serializer = UserProfileSerializer(users, many=True)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/usersmanagement/users/', format='json')
        self.assertEqual(response.data, serializer.data)

    def test_US2_I1_userlist_get_without_perm(self):
        """
            Test if a user without permission can't view the users' list.

            Inputs:

            Expected Output:
                We expect a 401 status code in the response.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/usersmanagement/users/', format='json')
        self.assertEqual(response.status_code, 401)

    def test_US2_I2_userlist_post_is_first_user_without_perm(self):
        """
            Test if a user without permission but it's first user can add an user.

            Inputs:
                post data (UserProfile): a mock-up for an user.

            Expected Output:
                We expect a 201 status code in the respone.
        """
        client = APIClient()
        client.login(username='tom', password='truc')
        response = client.post(
            '/api/usersmanagement/users/', {
                'username': 'joey',
                'password': 'machin'
            }, format='json'
        )
        self.assertEqual(response.status_code, 201)

    def test_US2_I2_userlist_post_with_perm(self):
        """
            Test if a user with permission can add an user.

            Inputs:
                post data (UserProfile): a mock-up for an user.

            Expected Output:
                We expect a 201 status code in the response.
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            '/api/usersmanagement/users/', {
                'username': 'joey',
                'password': 'machin',
                'email': 'test@pic.brasserie-du-slalom.fr'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)

    def test_US2_I2_userlist_post_without_perm(self):
        """
            Test if a user without permission can't add an user.

            Inputs:
                post data (UserProfile): a mock-up for an user.

            Expected Output:
                We expect an error in the response.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            '/api/usersmanagement/users/', {
                'username': 'joey',
                'password': 'machin',
                'email': 'test@pic.brasserie-du-slalom.fr'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_US2_I6_isfirstuserrequest_with_no_user(self):
        """
            Test if a is_first_user request works well

            Inputs:
               None

            Expected Output:
                We expect that the Response is True as there is no user in the database
        """
        client = APIClient()
        UserProfile.objects.all().delete()
        request = client.get('/api/usersmanagement/users/is_first_user', format='json')
        self.assertEqual(request.data, True)

    def test_US2_I6_isfirstuserrequest_with_user(self):
        """
            Test if a is_first_user request works well

            Inputs:
               None

            Expected Output:
                We expect that the Response is False as there is an user in the database
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        request = client.get('/api/usersmanagement/users/is_first_user', format='json')
        self.assertEqual(request.data, False)

    def test_US2_I7_usernamesuffix_with_existant(self):
        """
            Test if we get the correct suffix for the username

            Inputs:
               None

            Expected Output:
                We expect that the Response is 1 as there is an user in the database
                with the same username
        """
        user = self.set_up_perm()
        c = Client()
        response = c.get('/api/usersmanagement/users/username_suffix?username=tom')
        self.assertEqual(response.data, '1')

    def test_US2_I7_usernamesuffix_without_existant(self):
        """
            Test if we get the correct suffix for the username

            Inputs:
               None

            Expected Output:
                We expect that the Response is "" as there is no user in the database
                with the same username
        """
        c = Client()
        response = c.get('/api/usersmanagement/users/username_suffix?username=yolo')
        self.assertEqual(response.data, "")

    def test_US2_I3_userdetail_get_own_detail(self):
        """
            Test if a user without permission can view it's own details.

            Inputs:
                None

            Expected Output:
                We expect to get it's details in the response.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/usersmanagement/users/' + str(user.pk) + '/')
        self.assertEqual(response.data['username'], 'tom')

    def test_US2_I3_userdetail_get_with_perm(self):
        """
            Test if a user with permission can view an user.

            Inputs:
                None.

            Expected Output:
                We expect to get the user's details in the response..
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/usersmanagement/users/', {
                'username': 'joey',
                'password': 'machin'
            }, format='json'
        )
        pk = response1.data['id']
        response = client.get('/api/usersmanagement/users/' + str(pk) + '/')
        self.assertEqual(response.data['username'], 'joey')

    def test_US2_I3_userdetail_get_without_perm(self):
        """
            Test if a user without permission can't view an user.

            Inputs:

            Expected Output:
                We expect a 401 status code in the response.
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/usersmanagement/users/', {
                'username': 'joey',
                'password': 'machin'
            }, format='json'
        )
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.get('/api/usersmanagement/users/' + str(pk) + '/')
        self.assertEqual(response.status_code, 401)

    def test_US2_I4_userdetail_put_own_detail(self):
        """
            Test if a user without permission can change it's own details.

            Inputs:
                put data (JSON): a mock-up of an updated user.

            Expected Output:
                We expect to find updated user.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.put(
            '/api/usersmanagement/users/' + str(user.pk) + '/', {'first_name': 'Paul'}, format='json'
        )
        self.assertEqual(response.data['first_name'], 'Paul')

    def test_US2_I4_userdetail_put_with_perm(self):
        """
            Test if a user with permission can change an user.

            Inputs:
                put data (JSON): a mock-up of an updated user.

            Expected Output:
                We expect to find updated user.
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/usersmanagement/users/', {
                'username': 'joey',
                'password': 'machin',
                'first_name': 'Joey',
                'email': 'test@pic.brasserie-du-slalom.fr'
            },
            format='json'
        )
        pk = response1.data['id']
        response = client.put('/api/usersmanagement/users/' + str(pk) + '/', {'first_name': 'Paul'}, format='json')
        self.assertEqual(response.data['first_name'], 'Paul')

    def test_US2_I4_userdetail_put_without_perm(self):
        """
            Test if a user without permission can't change an user's informations

            Inputs:
                put data (JSON): a mock-up of an updated user.

            Expected Output:
                We expect a 401 status code in the response.
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/usersmanagement/users/', {
                'username': 'joey',
                'password': 'machin',
                'first_name': 'Joey',
                'email': 'test@pic.brasserie-du-slalom.fr'
            },
            format='json'
        )
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.put('/api/usersmanagement/users/' + str(pk) + '/', {'first_name': 'Paul'}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_US2_I5_userdetail_delete_with_perm(self):
        """
            Test if a user with permission can delete an user.

            Inputs:
                delete data (JSON): the id of the user to be deleted.

            Expected Output:
                We expect a 204 status code in the response.
                We expect to not find deleted user.
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/usersmanagement/users/', {
                'username': 'joey',
                'password': 'machin',
                'first_name': 'Joey',
                'email': 'test@pic.brasserie-du-slalom.fr'
            },
            format='json'
        )
        pk = response1.data['id']
        response = client.delete('/api/usersmanagement/users/' + str(pk) + '/')
        self.assertEqual(response.status_code, 204)

    def test_US2_I5_userdetail_delete_without_perm(self):
        """
            Test if a user without permission can't delete an user.

            Inputs:
                delete data (JSON): the id of the user to be deleted.

            Expected Output:
                We expect a 401 status code in the response.
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/usersmanagement/users/', {
                'username': 'joey',
                'password': 'machin',
                'first_name': 'Joey',
                'email': 'test@pic.brasserie-du-slalom.fr'
            },
            format='json'
        )
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.delete('/api/usersmanagement/users/' + str(pk) + '/')
        self.assertEqual(response.status_code, 401)

    def test_US2_I8_getuserpermissions_with_perm(self):
        """
            Test if a user with permission can view the permissions of an user.

            Inputs:
                None

            Expected Output:
                We expect to get in the response the correct permissions of the requested user
        """
        user = self.set_up_perm()
        pk = UserProfile.objects.get(username='tom').pk
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/usersmanagement/users/' + str(pk) + '/get_user_permissions')
        self.assertEqual(len(response.data), 4)

    def test_US2_I8_getuserpermissions_own_perm(self):
        """
            Test if a user without permission can view it's own permissions

            Inputs:
                None

            Expected Output:
                We expect to get in the response the correct permissions of the requested user
        """
        user = self.set_up_without_perm()
        pk = UserProfile.objects.get(username='tom').pk
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/usersmanagement/users/' + str(pk) + '/get_user_permissions')
        self.assertEqual(len(response.data), 0)

    def test_US2_I8_getuserpermissions_without_perm(self):
        """
            Test if a user without permission can't view the permissions of an user.

            Inputs:

            Expected Output:
                We expect a 401 status code in the response.
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response1 = client.post(
            '/api/usersmanagement/users/', {
                'username': 'joey',
                'password': 'machin'
            }, format='json'
        )
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.get('/api/usersmanagement/users/' + str(pk) + '/get_user_permissions')
        self.assertEqual(response.status_code, 401)

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

        user = UserProfile.objects.all()[0]

        self.assertEqual(user.groups.all().count(), 1)
        self.assertEqual(Team.objects.all().count(), 3)
        self.assertEqual(TeamType.objects.all().count(), 3)
        self.assertEqual('usersmanagement.add_userprofile' in user.get_all_permissions(), True)
