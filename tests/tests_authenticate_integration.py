from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient, APIRequestFactory
from usersmanagement.models import Team, TeamType, UserProfile
from usersmanagement.views.views_user import SignOut


class AuthentificationTests(TestCase):

    def set_up(self):
        user = UserProfile.objects.create(username='tom', password='truc')
        user.set_password('truc')
        user.save()
        return user

    def test_is_connected_with_correct_identifier_but_no_team(self):
        """
        Test if a user with correct identifier can connect.

                Inputs:
                    user (UserProfile): A UserProfile we create with no team assigned.

                Expected outputs:
                    We expect a 200 status code in the response.
                    We expect to find the pair {'error': 'User has no team'} in the error of the response's data.
        """

        user = self.set_up()
        client = APIClient()
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=truc',
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['error']['error'], 'User has no team')

    def test_is_connected_with_correct_identifier(self):
        """
        Test if a user with correct identifier can connect.

                Inputs:
                    user (UserProfile): a UserProfile we created and that is associated with team.
                    team (Team): a Team created so that user could be assigned to a Team.

                Excpected outputs:
                    We expect to find the pair {'success': 'True'} in the data of the response's data.
        """

        user = self.set_up()
        teamtype = TeamType.objects.create(name='TeamType test')
        team = Team.objects.create(team_type=teamtype)
        user.groups.add(team)
        user.save()
        client = APIClient()
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=truc',
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.data['data']['success'], 'True')

    def test_is_not_connected_with_incorrect_identifier(self):
        """
        Test if a user with incorrect identifier can't connect.

                Inputs:
                    user (UserProfile): a UserProfile we created and that we will try to login with the wrong password.

                Expected Outputs:
                    We expect to find the pair {'success': 'False'} in the error of the response's data.
                    We expect to find the pair {'error': 'Incorrect Password'} in the error of the response's data.
        """
        user = self.set_up()
        client = APIClient()
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.data['error']['success'], 'False')
        self.assertEqual(response.data['error']['error'], 'Incorrect password')

    def test_is_not_connected_nbtries_3(self):
        """
        Test if a user trying to connect three times with wrong password has a number of tries to three.

                Inputs:
                    user (UserProfile): a UserProfile we created and that we will block by sending three times a wrong password.

                Expected Outputs:
                    We expect to find the pair {'success': 'False'} in the error of the response's data.
                    We expect to find the pair {'is_blocked': 'True'} in the error of the response's data.
                    We expect to find the pair {'error': 'Wrong password 3 times in a row. You are blocked.'} in the error of the response's data.
                    We expect user to have its nb_tries equals to 3.
                    We expect user to have its is_actiave to be False.
        """

        user = self.set_up()
        client = APIClient()
        client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )
        client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.data['error']['success'], 'False')
        self.assertEqual(response.data['error']['is_blocked'], 'True')
        self.assertEqual(response.data['error']['error'], 'Wrong password 3 times in a row. You are blocked.')

        user = UserProfile.objects.get(pk=user.pk)
        self.assertEqual(user.nb_tries, 3)
        self.assertIs(user.is_active, False)

    def test_is_blocked_cant_connect(self):
        """
        Test if a blocked user can't connect with correct identifier.

                Inputs:
                    user (UserProfile): a UserProfile we created and that we will block by sending three times a wrong password.
                        We will attempt a fourth connection with the right data.

                Expected Outputs:
                    We expect to find the pair {'success': 'False'} in the error of the response's data.
                    We expect to find the pair {'is_blocked': 'True'} in the error of the response's data.
                    We expect to find the pair {'error': 'You have entered a wrong password too many times. You are blocked.'} in the error of the response's data.

        """
        user = self.set_up()
        client = APIClient()
        client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )
        client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )
        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=machin',
            content_type='application/x-www-form-urlencoded'
        )

        self.assertEqual(response.data.get("error").get("success"), 'False')
        self.assertEqual(response.data.get("error").get("is_blocked"), 'True')
        self.assertEqual(response.data.get("error").get("error"), "Wrong password 3 times in a row. You are blocked.")
        user = UserProfile.objects.get(pk=user.pk)
        self.assertEqual(user.nb_tries, 3)  # we let those assert to be sure that this step is valid before pursuing.

        response = client.post(
            '/api/usersmanagement/login',
            'username=tom&password=truc',
            content_type='application/x-www-form-urlencoded'
        )

        self.assertEqual(response.data['error']['success'], 'False')
        self.assertEqual(response.data['error']['is_blocked'], 'True')
        self.assertEqual(
            response.data['error']['error'], 'You have entered a wrong password too many times. You are blocked.'
        )

    def test_sign_out(self):
        """
        Test if a user can logout.

                Inputs:
                    user (UserProfile): a UserProfile we created and that we will connect before disconnecting.

                Expected Output:
                    We expect to find True in the response's data.
        """
        self.set_up()
        factory = APIRequestFactory()
        request = factory.get('/gestion/logout')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        sign_out = SignOut()
        response = sign_out.get(request)
        self.assertIs(response.data, True)
