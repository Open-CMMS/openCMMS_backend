from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from maintenancemanagement.models import (
    Equipment, EquipmentType, Field, FieldGroup, FieldObject, FieldValue, Task,
)
from maintenancemanagement.serializers import FieldObjectSerializer
from openCMMS import settings
from rest_framework.test import APIClient
from usersmanagement.models import UserProfile

User = settings.AUTH_USER_MODEL


class FieldObjectTests(TestCase):
    """
    Tests on FieldObject views
    """

    def setUp(self):
        """
        Set-up FieldGroup, Field, FieldValue and FieldObject for the tests
        """
        field_maintenance = FieldGroup.objects.create(name="Maintenance")
        des_conditions = Field.objects.create(
            name="Des Conditions", field_group=field_maintenance
        )
        condition_date = FieldValue.objects.create(value="Date", field=des_conditions)
        condition_duree = FieldValue.objects.create(value="Durée", field=des_conditions)
        une_tache = Task.objects.create(name="uneTache")
        typeE = EquipmentType.objects.create(name="Type d'equipement")
        un_equipment = Equipment.objects.create(
            name="unEquipement", equipment_type=typeE
        )
        FieldObject.objects.create(
            content_type=ContentType.objects.get(model="task"),
            object_id=une_tache.id,
            field=des_conditions,
            field_value=condition_date,
            value="02/05/2020",
            description="Date",
        )
        FieldObject.objects.create(
            content_type=ContentType.objects.get(model="equipment"),
            object_id=un_equipment.id,
            field=des_conditions,
            field_value=condition_duree,
            value="02/05/2020",
            description="Date",
        )

    def add_view_perm(self, user):
        """
        Add view permission to user
        """
        perm_view = Permission.objects.get(codename="view_fieldobject")
        user.user_permissions.set([perm_view])

    def add_add_perm(self, user):
        """
        Add add permission to user
        """
        perm_add = Permission.objects.get(codename="add_fieldobject")
        user.user_permissions.set([perm_add])

    def add_update_perm(self, user):
        """
        Add update permission to user
        """
        perm_update = Permission.objects.get(codename="change_fieldobject")
        user.user_permissions.set([perm_update])

    def add_delete_perm(self, user):
        """
        Add update permission to user
        """
        perm_delete = Permission.objects.get(codename="delete_fieldobject")
        user.user_permissions.set([perm_delete])

    def test_fieldObject_list_get_authorized(self):
        """
        Test if a fieldObject_list in GET return all the fieldObject and HTTP200 for a authorized user.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        fieldobjects = FieldObject.objects.all()
        serializer = FieldObjectSerializer(fieldobjects, many=True)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/maintenancemanagement/fieldobjects/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_fieldObject_list_get_unauthorized(self):
        """
        Test if fieldObject_list view in GET return HTTP 401 for a unauthorized user.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/maintenancemanagement/fieldobjects/")
        self.assertEqual(response.status_code, 401)

    def test_fieldObject_list_post_authorized(self):
        """
        Test if fieldObject_list view in POST add a fieldObject and return HTTP 201
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        une_tache = Task.objects.get(name="uneTache")
        des_conditions = Field.objects.get(name="Des Conditions")
        condition_date = FieldValue.objects.get(value="Durée")
        data = {
            "described_object": "Task: " + str(une_tache.id),
            "field": des_conditions.id,
            "field_value": condition_date.id,
            "value": "02/03/20",
            "description": "Date de test",
        }
        response = c.post(
            "/api/maintenancemanagement/fieldobjects/", data, format="json"
        )
        fo = FieldObject.objects.get(description="Date de test")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(FieldObject.objects.filter(description="Date de test"))
        self.assertEqual(fo.described_object, Task.objects.get(id=une_tache.id))

    def test_fieldObject_list_post_unauthorized(self):
        """
        Test if fieldObject_list view in POST return HTTP 401 for a unauthorized user.
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        data = {
            "described_object": "Task: 1",
            "field": 1,
            "field_value": 1,
            "value": "02/03/20",
            "description": "Date de test",
        }
        response = c.post(
            "/api/maintenancemanagement/fieldobjects/", data, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_fieldObject_details_get_authorized(self):
        """
        Test if a user with authorization can see a fieldObject's details
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        fo = FieldObject.objects.get(
            content_type=ContentType.objects.get(model="equipment")
        )
        response = c.get(f"/api/maintenancemanagement/fieldobjects/{fo.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, FieldObjectSerializer(fo).data)

    def test_fieldObject_details_get_unauthorized(self):
        """
        Test if a user without authorization can't see a fieldObject's details
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        fo = FieldObject.objects.get(
            content_type=ContentType.objects.get(model="equipment")
        )
        response = c.get(f"/api/maintenancemanagement/fieldobjects/{fo.pk}/")
        self.assertEqual(response.status_code, 401)

    def test_fieldObject_details_put_authorized(self):
        """
        Test if a user with authorization can update a fieldObject
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_update_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        fo = FieldObject.objects.get(
            content_type=ContentType.objects.get(model="equipment")
        )
        une_tache = Task.objects.get(name="uneTache")
        des_conditions = Field.objects.get(name="Des Conditions")
        data = {
            "described_object": "Task: " + str(une_tache.id),
            "field": des_conditions.id,
        }
        response = c.put(
            f"/api/maintenancemanagement/fieldobjects/{fo.pk}/", data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["described_object"], data["described_object"])
        self.assertEqual(response.data["field"], data["field"])

    def test_fieldObject_details_put_unauthorized(self):
        """
        Test if a user without authorization can't update a fieldObject
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        fo = FieldObject.objects.get(content_type=ContentType.objects.get(model="task"))
        data = {"described_object": "Task: 1", "field": 1}
        response = c.put(
            f"/api/maintenancemanagement/fieldobjects/{fo.pk}/", data, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_fieldObject_details_delete_authorized(self):
        """
        Test if a user with authorization can delete a fieldObject
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_delete_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        fo = FieldObject.objects.get(
            content_type=ContentType.objects.get(model="equipment")
        )
        response = c.delete(f"/api/maintenancemanagement/fieldobjects/{fo.pk}/")
        self.assertEqual(response.status_code, 204)

    def test_fieldObject_details_delete_unauthorized(self):
        """
        Test if a user without authorization can't delete a fieldObject
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        fo = FieldObject.objects.get(
            content_type=ContentType.objects.get(model="equipment")
        )
        response = c.delete(f"/api/maintenancemanagement/fieldobjects/{fo.pk}/")
        self.assertEqual(response.status_code, 401)
