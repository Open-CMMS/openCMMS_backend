from django.contrib.auth.models import Permission
from django.test import TestCase
from maintenancemanagement.models import Field, FieldGroup
from maintenancemanagement.serializers import FieldSerializer
from openCMMS import settings
from rest_framework.test import APIClient
from usersmanagement.models import UserProfile

User = settings.AUTH_USER_MODEL


class FieldTests(TestCase):
    """
    Tests for Field views.
    """

    def set_up_fieldGroup(self):
        """
        Set-up FieldGroup for the tests
        """
        a_field_group = FieldGroup.objects.create(name="aFieldGroup", is_equipment=True)
        return a_field_group

    def add_view_perm(self, user):
        """
        Add view permission to user
        """
        perm_view = Permission.objects.get(codename="view_field")
        user.user_permissions.set([perm_view])

    def test_field_list_get_authorized(self):
        """
        Test if field_list view return all the field in a list and HTTP 200 for a authorized user.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        a_field_group = self.set_up_fieldGroup()
        Field.objects.create(name="oneField", field_group=a_field_group)
        serializer = FieldSerializer(Field.objects.all(), many=True)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/maintenancemanagement/fields/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_field_list_get_unauthorized(self):
        """
        Test if field_list view return all the field in a list and HTTP 401 for a unauthorized user.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/maintenancemanagement/fields/")
        self.assertEqual(response.status_code, 401)
