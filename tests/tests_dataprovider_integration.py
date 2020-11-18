import os

import pytest
from init_db_tests import init_db

from django.contrib.auth.models import Permission
from django.test import TestCase, client
from maintenancemanagement.models import Equipment, Field, FieldObject
from openCMMS.settings import BASE_DIR
from rest_framework.test import APIClient
from usersmanagement.models import UserProfile
from utils.models import DataProvider
from utils.serializers import (
    DataProviderRequirementsSerializer,
    DataProviderSerializer,
)


class DataProviderTest(TestCase):

    @pytest.fixture(scope="class", autouse=True)
    def init_database(django_db_setup, django_db_blocker):
        with django_db_blocker.unblock():
            init_db()

    def add_view_perm(self, user):
        """
            Add view permission to user
        """
        perm_view = Permission.objects.get(codename="view_dataprovider")
        user.user_permissions.set([perm_view])

    def add_add_perm(self, user):
        """
            Add add permission to user
        """
        perm_add = Permission.objects.get(codename="add_dataprovider")
        user.user_permissions.add(perm_add)

    def add_change_perm(self, user):
        """
            Add change permission to user
        """
        perm_change = Permission.objects.get(codename="change_dataprovider")
        user.user_permissions.set([perm_change])

    def add_delete_perm(self, user):
        """
            Add delete permission to user
        """
        perm_delete = Permission.objects.get(codename="delete_dataprovider")
        user.user_permissions.set([perm_delete])

    def test_US23_I1_dataproviderlist_get_with_perm(self):
        """
            Test if a user with perm receive the dataproviders' list
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        python_files = os.listdir(os.path.join(BASE_DIR, 'utils/data_providers'))
        python_files.pop(python_files.index('__init__.py'))
        if '__pycache__' in python_files:
            python_files.pop(python_files.index('__pycache__'))
        equipments = Equipment.objects.all()
        data_providers = DataProvider.objects.all()
        serializer = DataProviderRequirementsSerializer({'equipments': equipments, 'data_providers': data_providers})
        dict_res = serializer.data.copy()
        dict_res['python_files'] = python_files
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/dataproviders/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict_res, response.json())

    def test_US23_I1_dataproviderlist_get_without_perm(self):
        """
            Test if a user without perm doesn't receive the dataproviders' list
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/dataproviders/")
        self.assertEqual(response.status_code, 401)

    def test_US23_I2_dataproviderlist_post_with_perm(self):
        """
            Test if a user with perm can add a dataprovider
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            '/api/dataproviders/', {
                'file_name': 'python_file.py',
                'name': 'dataprovider de test',
                'recurrence': '10d',
                'ip_address': '127.0.0.1',
                'equipment': Equipment.objects.get(name='Embouteilleuse AXB1').id,
                'field_object': Field.objects.get(name="Nb bouteilles").object_set.get().id,
                'is_activated': True
            },
            format='json'
        )
        dataprovider = DataProvider.objects.get(file_name='python_file.py')
        serializer = DataProviderSerializer(dataprovider)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, serializer.data)

    def test_US23_I2_dataproviderlist_post_without_perm(self):
        """
            Test if a user without perm can't add a dataprovider
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            '/api/dataproviders/', {
                'file_name': 'script.py',
                'name': 'dataprovider de test',
                'recurrence': '10d',
                'ip_address': '127.0.0.1',
                'equipment': Equipment.objects.get(name='Embouteilleuse AXB1').id,
                'field_object': Field.objects.get(name="Nb bouteilles").object_set.get().id,
                'is_activated': True
            },
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_US23_I2_dataproviderlist_post_with_perm_and_missing_parms(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            '/api/dataproviders/', {
                'file_name': 'script.py',
                'equipment': Equipment.objects.get(name='Embouteilleuse AXB1').id,
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_US23_I2_dataproviderlist_post_with_perm_and_too_much_parms(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            '/api/dataproviders/', {
                'file_name': 'script.py',
                'name': 'dataprovider de test',
                'recurrence': '10d',
                'ip_address': '127.0.0.1',
                'equipment': Equipment.objects.get(name='Embouteilleuse AXB1').id,
                'field_object': Field.objects.get(name="Nb bouteilles").object_set.get().id,
                'fake field': 'useless data',
                'is_activated': True
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        dataprovider = DataProvider.objects.get(file_name='script.py')
        serializer = DataProviderSerializer(dataprovider)
        self.assertEqual(response.data, serializer.data)

    def test_US23_I3_dataproviderdetail_get_with_perm(self):
        """
            Test if a user with perm can get a dataprovider.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        client = APIClient()
        client.force_authenticate(user=user)
        dataprovider = DataProvider.objects.get(file_name="fichier_test_dataprovider.py")
        serializer = DataProviderSerializer(dataprovider)
        response = client.get(f'/api/dataproviders/{dataprovider.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def test_US23_I3_dataproviderdetail_get_without_perm(self):
        """
            Test if a user with perm can get a dataprovider.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        client = APIClient()
        client.force_authenticate(user=user)
        dataprovider = DataProvider.objects.get(file_name="fichier_test_dataprovider.py")
        response = client.get(f'/api/dataproviders/{dataprovider.id}/')
        self.assertEqual(response.status_code, 401)

    def test_US23_I4_dataproviderdetail_put_with_perm(self):
        """
            Test if a user with perm can update a dataprovider.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_change_perm(user)
        self.add_add_perm(user)
        client = APIClient()
        client.force_authenticate(user=user)
        client.post(
            '/api/dataproviders/', {
                'file_name': 'python_file.py',
                'name': 'dataprovider de test pour put',
                'recurrence': '10d',
                'ip_address': '127.0.0.1',
                'equipment': Equipment.objects.get(name='Embouteilleuse AXB1').id,
                'field_object': Field.objects.get(name="Nb bouteilles").object_set.get().id,
                'is_activated': True
            },
            format='json'
        )
        dataprovider = DataProvider.objects.get(name='dataprovider de test pour put')
        response = client.put(
            f'/api/dataproviders/{dataprovider.id}/', {
                'file_name': 'fichier_test_dataprovider.py',
                'name': 'dataprovider mis à jour',
                'recurrence': '5d',
                'ip_address': '192.168.0.1',
                'equipment': Equipment.objects.get(name='Embouteilleuse AXB1').id,
                'field_object': Field.objects.get(name="Nb bouteilles").object_set.get().id,
                'is_activated': True
            },
            format='json'
        )
        dataprovider = DataProvider.objects.get(name='dataprovider mis à jour')
        serializer = DataProviderSerializer(dataprovider)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def test_US23_I4_dataproviderdetail_put_with_perm_and_missing_parms(self):
        """
            Test if a user with perm can update a dataprovider.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_change_perm(user)
        self.add_add_perm(user)
        client = APIClient()
        client.force_authenticate(user=user)
        client.post(
            '/api/dataproviders/', {
                'file_name': 'python_file.py',
                'name': 'dataprovider de test pour put',
                'recurrence': '10d',
                'ip_address': '127.0.0.1',
                'equipment': Equipment.objects.get(name='Embouteilleuse AXB1').id,
                'field_object': Field.objects.get(name="Nb bouteilles").object_set.get().id,
                'is_activated': True
            },
            format='json'
        )
        dataprovider = DataProvider.objects.get(name='dataprovider de test pour put')
        response = client.put(
            f'/api/dataproviders/{dataprovider.id}/', {
                'name': 'dataprovider mis à jour 2',
                'ip_address': '192.168.1.2',
            },
            format='json'
        )
        dataprovider = DataProvider.objects.get(name='dataprovider mis à jour 2')
        serializer = DataProviderSerializer(dataprovider)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def test_US23_I5_dataproviderdetail_delete_with_perm(self):
        """
            Test if a user with perm can delete a dataprovider.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_delete_perm(user)
        client = APIClient()
        client.force_authenticate(user=user)
        dataprovider = DataProvider.objects.get(file_name="fichier_test_dataprovider.py")
        response = client.delete(f'/api/dataproviders/{dataprovider.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(DataProvider.objects.filter(id=dataprovider.id).exists())

    def test_US23_I5_dataproviderdetail_delete_without_perm(self):
        """
            Test if a user without perm can't delete a dataprovider.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        client = APIClient()
        client.force_authenticate(user=user)
        dataprovider = DataProvider.objects.get(file_name="fichier_test_dataprovider.py")
        response = client.delete(f'/api/dataproviders/{dataprovider.id}/')
        self.assertEqual(response.status_code, 401)

    def test_US23_I6_testdataprovider_post_with_perm(self):
        """
            Test if a user with perm can test a data provider.
        """
        with open(os.path.join(BASE_DIR, 'utils/data_providers/temp_test_data_providers.py'), "w+") as file:
            file.write('def get_data(ip_address):\n')
            file.write('    return 2')
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            f'/api/dataproviders/test/', {
                'file_name': 'temp_test_data_providers.py',
                'name': 'dataprovider de test',
                'recurrence': '10d',
                'ip_address': '127.0.0.1',
                'equipment': Equipment.objects.get(name='Embouteilleuse AXB1').id,
                'field_object': Field.objects.get(name="Nb bouteilles").object_set.get().id,
                'is_activated': True
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 2)
        os.remove(os.path.join(BASE_DIR, 'utils/data_providers/temp_test_data_providers.py'))

    def test_US23_I6_testdataprovider_post_without_perm(self):
        """
             Test if a user without perm can't test a data provider.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(f'/api/dataproviders/test/', format='json')
        self.assertEqual(response.status_code, 401)

    def test_US23_I6_testdataprovider_post_with_perm_and_not_well_formated_file(self):
        """
            Test if a user with perm can test a data provider with a not well formted file.
        """
        with open(os.path.join(BASE_DIR, 'utils/data_providers/temp_test_data_providers_error.py'), "w+") as file:
            file.write('def wrong_get_data(ip_address):\n')
            file.write('    return 2')
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            f'/api/dataproviders/test/', {
                'file_name': 'temp_test_data_providers_error.py',
                'name': 'dataprovider de test',
                'recurrence': '10d',
                'ip_address': '127.0.0.1',
                'equipment': Equipment.objects.get(name='Embouteilleuse AXB1').id,
                'field_object': Field.objects.get(name="Nb bouteilles").object_set.get().id,
                'is_activated': True
            },
            format='json'
        )
        self.assertEqual(response.status_code, 501)
        self.assertEqual(response.data, 'Python file is not well formated, please follow the example')
        os.remove(os.path.join(BASE_DIR, 'utils/data_providers/temp_test_data_providers_error.py'))

    def test_US23_I6_testdataprovider_post_with_perm_but_not_file(self):
        """
            Test if a user with perm can test a data provider with a not well formted file.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            f'/api/dataproviders/test/', {
                'file_name': 'toto.py',
                'name': 'dataprovider de test',
                'recurrence': '10d',
                'ip_address': '127.0.0.1',
                'equipment': Equipment.objects.get(name='Embouteilleuse AXB1').id,
                'field_object': Field.objects.get(name="Nb bouteilles").object_set.get().id,
                'is_activated': True
            },
            format='json'
        )
        self.assertEqual(response.status_code, 501)
        self.assertEqual(response.data, "Python file not found, please enter 'name_of_your_file.py'")

    def test_US23_I6_testdataprovider_post_with_perm_and_not_working_get_data(self):
        """
            Test if a user with perm can test a data provider with a not working get_data function.
        """
        with open(
            os.path.join(BASE_DIR, 'utils/data_providers/temp_test_data_providers_error_in_getdata.py'), "w+"
        ) as file:
            file.write('from utils.data_provider import GetDataException\n')
            file.write('def get_data(ip_address):\n')
            file.write('    raise GetDataException()')
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            f'/api/dataproviders/test/', {
                'file_name': 'temp_test_data_providers_error_in_getdata.py',
                'name': 'dataprovider de test',
                'recurrence': '10d',
                'ip_address': '127.0.0.1',
                'equipment': Equipment.objects.get(name='Embouteilleuse AXB1').id,
                'field_object': Field.objects.get(name="Nb bouteilles").object_set.get().id,
                'is_activated': True
            },
            format='json'
        )
        self.assertEqual(response.status_code, 501)
        self.assertEqual(response.data, 'IP not found or python file not working')
        os.remove(os.path.join(BASE_DIR, 'utils/data_providers/temp_test_data_providers_error_in_getdata.py'))
