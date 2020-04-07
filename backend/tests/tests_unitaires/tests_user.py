from django.urls import reverse
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import Permission
from gestion.models import User_Profile
from rest_framework.test import APIClient

class UserTests(TestCase):


    def test_can_acces_users_list(self):
        client = APIClient()
        client.login(username='JoranMarie1', password='p@sword-au-top')
        response = client.get('/gestion/users/', format='json')
        print(response.data)

    
        

