from django.contrib.auth.models import Permission
from django.test import TestCase
from maintenancemanagement.models import Field, FieldGroup, FieldValue
from maintenancemanagement.serializers import FieldValueSerializer
from openCMMS import settings
from rest_framework.test import APIClient
from usersmanagement.models import UserProfile

User = settings.AUTH_USER_MODEL


class FieldValueTests(TestCase):
    """
        Tests on FieldValue views
    """

    def setUp(self):
        """
            Set-up FieldGroup, Field and FieldValues for the tests
        """
        field_maintenance = FieldGroup.objects.create(name="Maintenance")
        des_conditions = Field.objects.create(name="Des Conditions", field_group=field_maintenance)
        FieldValue.objects.create(value="Date", field=des_conditions)
        FieldValue.objects.create(value="Durée", field=des_conditions)

    def add_view_perm(self, user):
        """
            Add view permission to user
        """

        perm_view = Permission.objects.get(codename="view_fieldvalue")
        user.user_permissions.set([perm_view])

    def test_field_value_for_field_get_authorized(self):
        """
            Test if field_value_for_field view in GET return all the fieldValues in a list and HTTP 200 for a authorized user.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        fields_value = [FieldValue.objects.get(value="Date"), FieldValue.objects.get(value="Durée")]
        serializer = FieldValueSerializer(fields_value, many=True)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get(
            "/api/maintenancemanagement/fieldvalues_for_field/" + str(Field.objects.get(name="Des Conditions").id) +
            "/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_field_value_for_field_get_unauthorized(self):
        """
            Test if field_value_for_field view in GET return HTTP 401 for a unauthorized user.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get(
            "/api/maintenancemanagement/fieldvalues_for_field/" + str(Field.objects.get(name="Des Conditions").id) +
            "/"
        )
        self.assertEqual(response.status_code, 401)
