from django.urls import reverse
from django.core.exceptions import ValidationError
from django.test import TestCase
from usersmanagement.models import UserProfile
from rest_framework.test import APIRequestFactory
from usersmanagement.views.views_user import sign_in, sign_out
from django.contrib.sessions.middleware import SessionMiddleware
from rest_framework.response import Response

class AuthentificationTests(TestCase):

    def set_up(self):
        user = UserProfile(username='tom')
        user.set_password('truc')
        user.save()
        return user

    def test_is_connected_with_correct_identifier(self):
        """
            Test if a user with correct identifier can connect
        """
        user = self.set_up()
        factory = APIRequestFactory()
        request = factory.post('/gestion/login', {'username': 'tom', 'password': 'truc'}, format='json')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        response = sign_in(request)
        self.assertEqual(response.data , (True, False, user.pk))

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
        self.assertEqual(response.data , (False, False, 0))

    def test_is_not_connected_nbtries_3(self):
        """
            Test if a user trying to connect three times with wrong password has a number of tries to three.
        """
        self.set_up()
        factory = APIRequestFactory()
        for i in range(3):
            request = factory.post('/gestion/login', {'username': 'tom', 'password': 'mavhin'}, format='json')
            middleware = SessionMiddleware()
            middleware.process_request(request)
            request.session.save()
            response = sign_in(request)
        user = UserProfile.objects.get(username='tom')
        self.assertEqual(response.data, (False, True, 0)) and self.assertEqual(user.nb_tries, 3)

    def test_is_blocked_nbtries_3(self):
        """
            Test if a user trying to connect three times with wrong password is blocked.
        """
        self.set_up()
        factory = APIRequestFactory()
        for i in range(3):
            request = factory.post('/gestion/login', {'username': 'tom', 'password': 'mavhin'}, format='json')
            middleware = SessionMiddleware()
            middleware.process_request(request)
            request.session.save()
            response = sign_in(request)
        user = UserProfile.objects.get(username='tom')
        self.assertEqual(response.data, (False, True, 0)) and self.assertEqual(user.is_active, False)

    def test_is_blocked_cant_connect(self):
        """
            Test if a blocked user can't connect with correct identifier.
        """
        self.set_up()
        factory = APIRequestFactory()
        for i in range(3):
            request = factory.post('/gestion/login', {'username': 'tom', 'password': 'mavhin'}, format='json')
            middleware = SessionMiddleware()
            middleware.process_request(request)
            request.session.save()
            response = sign_in(request)
        factory = APIRequestFactory()
        request_final = factory.post('/gestion/login', {'username': 'tom', 'password': 'truc'}, format='json')
        middleware_final = SessionMiddleware()
        middleware_final.process_request(request_final)
        request_final.session.save()
        response_final = sign_in(request_final)
        self.assertEqual(response_final.status_code , 401)

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
