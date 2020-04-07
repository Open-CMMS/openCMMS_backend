from django.urls import reverse
from django.core.exceptions import ValidationError
from django.test import TestCase
from gestion.models import User_Profile
from rest_framework.test import APIRequestFactory
from gestion.views import sign_in, sign_out
from django.contrib.sessions.middleware import SessionMiddleware
from rest_framework.response import Response

class AuthentificationTests(TestCase):

    def set_up(self):
        user = User_Profile(username='tom')
        user.set_password('truc')
        user.save()
        return user

    def test_is_connected_with_correct_identifier(self):
        """
            Test if a user with correct identifier can connect
        """
        self.set_up()
        factory = APIRequestFactory()
        request = factory.post('/gestion/login', {'username': 'tom', 'password': 'truc'}, format='json')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        response = sign_in(request)
        self.assertEqual(response.data , True)

    def test_is_not_connected_with_incorrect_identifier(self):
        """
            Test if a user with incorrect identifier can't connect
        """
        self.set_up()
        factory = APIRequestFactory()
        request = factory.post('/gestion/login', {'username': 'tom', 'password': 'mavhin'}, format='json')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        response = sign_in(request)
        self.assertEqual(response.data , False)

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
        response = sign_out(request)
        self.assertEqual(response.data , True)
