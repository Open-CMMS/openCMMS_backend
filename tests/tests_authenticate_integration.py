from usersmanagement.models import UserProfile
from usersmanagement.views.views_user import SignOut

from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient, APIRequestFactory


class AuthentificationTests(TestCase):

    def set_up(self):
        user = UserProfile.objects.create(username='tom', password='truc')
        user.set_password('truc')
        user.save()
        return user

    def test_is_connected_with_correct_identifier(self):
        """
            Test if a user with correct identifier can connect
        """

        user = self.set_up()
        client = APIClient()
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=truc',
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.data["success"], 'True')

    def test_is_not_connected_with_incorrect_identifier(self):
        """
            Test if a user with incorrect identifier can't connect
        """
        user = self.set_up()
        client = APIClient()
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.data["success"], 'False')
        self.assertEqual(response.data["error"], 'Mot de passe incorrect')

    def test_is_not_connected_nbtries_3(self):
        """
            Test if a user trying to connect three times with wrong password has a number of tries to three.
        """

        user = self.set_up()
        client = APIClient()
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.data["success"], 'False')
        self.assertEqual(response.data["is_blocked"], 'True')
        self.assertEqual(response.data["error"], "Mot de passe incorrect 3 fois de suite. Vous êtes bloqués.")

        user = UserProfile.objects.get(pk=user.pk)
        self.assertEqual(user.nb_tries, 3)

    def test_is_blocked_nbtries_3(self):
        """
            Test if a user trying to connect three times with wrong password is blocked.
        """
        user = self.set_up()
        client = APIClient()
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.data["success"], 'False')
        self.assertEqual(response.data["is_blocked"], 'True')
        self.assertEqual(response.data["error"], "Mot de passe incorrect 3 fois de suite. Vous êtes bloqués.")

        user = UserProfile.objects.get(pk=user.pk)
        self.assertEqual(user.is_active, False)

    def test_is_blocked_cant_connect(self):
        """
            Test if a blocked user can't connect with correct identifier.
        """
        user = self.set_up()
        client = APIClient()
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )

        self.assertEqual(response.data["success"], 'False')
        self.assertEqual(response.data["is_blocked"], 'True')
        self.assertEqual(response.data["error"], "Mot de passe incorrect 3 fois de suite. Vous êtes bloqués.")
        user = UserProfile.objects.get(pk=user.pk)
        self.assertEqual(user.nb_tries, 3)

        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=truc',
            content_type='application/x-www-form-urlencoded'
        )

        self.assertEqual(response.data["success"], 'False')
        self.assertEqual(response.data["is_blocked"], 'True')
        self.assertEqual(
            response.data["error"], "Vous vous êtes trompés trop de fois de mot de passe. Vous êtes bloqués."
        )

    def test_sign_out(self):
        """
            Test if a user can logout
        """
        self.set_up()
        factory = APIRequestFactory()
        request = factory.get('/gestion/logout')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        sign_out = SignOut()
        response = sign_out.get(request)
        self.assertEqual(response.data, True)
