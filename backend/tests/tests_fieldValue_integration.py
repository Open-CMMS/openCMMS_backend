from django.test import TestCase
from django.contrib.auth.models import Permission
from rest_framework.test import APIClient
from openCMMS import settings
from usersmanagement.models import UserProfile
from maintenancemanagement.models import Field, FieldValue, FieldGroup
from maintenancemanagement.serializers import FieldValueSerializer

User = settings.AUTH_USER_MODEL


class FieldValueTests(TestCase):
    """
        Tests on FieldValue views
    """

    def setUp(self):
        field_maintenance = FieldGroup.objects.create(name="Maintenance")
        des_conditions = Field.objects.create(name="Des Conditions", field_group = field_maintenance)
        FieldValue.objects.create(value = "Date", field = des_conditions)
        FieldValue.objects.create(value = "Durée", field = des_conditions)

    def add_view_perm(self, user):
        perm_view = Permission.objects.get(codename="view_fieldvalue")
        user.user_permissions.set([perm_view])

    def test_fieldValue_for_field_get_authorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        fields_value = [FieldValue.objects.get(value="Date"), FieldValue.objects.get(value="Durée")]
        serializer = FieldValueSerializer(fields_value, many=True)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/maintenancemanagement/fieldvalues_for_field/"+str(Field.objects.get(name="Des Conditions").id)+"/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_fieldValue_for_field_get_unauthorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/maintenancemanagement/fieldvalues_for_field/"+str(Field.objects.get(name="Des Conditions").id)+"/")
        self.assertEqual(response.status_code, 401)
