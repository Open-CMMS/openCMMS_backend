import pytest
from init_db_tests import init_db

from django.contrib.auth.models import Permission
from django.test import TestCase, client
from maintenancemanagement.models import Equipment, Field, FieldObject
from rest_framework.test import APIClient
from usersmanagement.models import UserProfile
from utils.models import Plugin
from utils.serializers import PluginSerializer


class PluginTest(TestCase):

    @pytest.fixture(scope="class", autouse=True)
    def init_database(django_db_setup, django_db_blocker):
        with django_db_blocker.unblock():
            init_db()

    def add_view_perm(self, user):
        """
            Add view permission to user
        """
        perm_view = Permission.objects.get(codename="view_plugin")
        user.user_permissions.set([perm_view])

    def add_add_perm(self, user):
        """
            Add add permission to user
        """
        perm_add = Permission.objects.get(codename="add_plugin")
        user.user_permissions.add(perm_add)

    def test_US23_I1_get_pluginlist_get_with_perm(self):
        """
            Test if a user with perm receive the plugins' list
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        plugin = Plugin.objects.all()
        serializer = PluginSerializer(plugin, many=True)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/plugins/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_US23_I1_get_pluginlist_get_without_perm(self):
        """
            Test if a user without perm doesn't receive the plugins' list
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/plugins/")
        self.assertEqual(response.status_code, 401)

    def test_US23_I2_get_pluginlist_post_with_perm(self):
        """
            Test if a user with perm can add a plugin
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            '/api/plugins/', {
                'file_name': 'python_file.py',
                'recurrence': '10d',
                'ip_address': '127.0.0.1',
                'equipment': Equipment.objects.get(name='Embouteilleuse AXB1').id,
                'field_object': Field.objects.get(name="Nb bouteilles").object_set.get().id
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)

    def test_US23_I2_get_pluginlist_post_without_perm(self):
        """
            Test if a user without perm can't add a plugin
        """
