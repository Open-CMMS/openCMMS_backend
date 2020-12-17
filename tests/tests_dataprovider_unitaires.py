import os

import pytest
from init_db_tests import init_db

from django.contrib.auth.models import Permission
from django.test import TestCase
from maintenancemanagement.models import Equipment, Field
from openCMMS.settings import BASE_DIR
from rest_framework.test import APIClient
from usersmanagement.models import UserProfile
from utils.data_provider import _trigger_dataprovider
from utils.models import DataProvider


class DataProviderTest(TestCase):

    @pytest.fixture(scope="class", autouse=True)
    def init_database(django_db_setup, django_db_blocker):
        with django_db_blocker.unblock():
            init_db()

    def add_add_perm(self, user):
        """
            Add add permission to user
        """
        perm_add = Permission.objects.get(codename="add_dataprovider")
        user.user_permissions.add(perm_add)

    def test_US23_U1_dataprovider_execution(self):
        """
            Test if a user with perm can test a data provider.

            Inputs:
                user (UserProfile): a UserProfile with permissions to add data providers.
                file (File): a temporary file which will return a value for the data provider test.
                post data (JSON): a mock-up of a data provider.

            Expected Output:
                We expect to get the updated value in the fieldObject after triggering the dataprovider.
        """
        with open(os.path.join(BASE_DIR, 'utils/data_providers/temp_test_data_providers.py'), "w+") as file:
            file.write('def get_data(ip_address, port):\n')
            file.write('    return 2')
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        client = APIClient()
        client.force_authenticate(user=user)
        client.post(
            f'/api/dataproviders/', {
                'file_name': 'temp_test_data_providers.py',
                'name': 'dataprovider de test',
                'recurrence': '10d',
                'ip_address': '127.0.0.1',
                'port': 5002,
                'equipment': Equipment.objects.get(name='Embouteilleuse AXB1').id,
                'field_object': Field.objects.get(name="Nb bouteilles").object_set.get().id,
                'is_activated': True
            },
            format='json'
        )
        dataprovider = DataProvider.objects.get(name='dataprovider de test')
        _trigger_dataprovider(dataprovider)
        self.assertEqual(int(Field.objects.get(name="Nb bouteilles").object_set.get().value), 2)
        os.remove(os.path.join(BASE_DIR, 'utils/data_providers/temp_test_data_providers.py'))
