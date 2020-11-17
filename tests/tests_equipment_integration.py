import pytest
from init_db_tests import init_db

from django.contrib.auth.models import Permission
from django.test import TestCase
from maintenancemanagement.models import (
    Equipment,
    EquipmentType,
    Field,
    FieldGroup,
    FieldObject,
    FieldValue,
)
from maintenancemanagement.serializers import (
    EquipmentDetailsSerializer,
    EquipmentSerializer,
)
from openCMMS import settings
from rest_framework.test import APIClient
from usersmanagement.models import UserProfile

User = settings.AUTH_USER_MODEL


class EquipmentTests(TestCase):

    @pytest.fixture(scope="class", autouse=True)
    def init_database(django_db_setup, django_db_blocker):
        with django_db_blocker.unblock():
            init_db()

    def setUp(self):
        """
            Set up an equipment with a name and an equipment type with or without fields
        """
        v = EquipmentType.objects.create(name="Voiture")
        Equipment.objects.create(name="Peugeot Partner", equipment_type=v)

        field_group = FieldGroup.objects.create(name="embouteilleuse", is_equipment=True)
        embouteilleuse = EquipmentType.objects.create(name="embouteilleuse")
        embouteilleuse.fields_groups.set([field_group])
        Field.objects.create(name="Capacité", field_group=field_group)
        Field.objects.create(name="Pression Normale", field_group=field_group)
        marque = Field.objects.create(name="marque", field_group=field_group)
        FieldValue.objects.create(value="Bosch", field=marque)
        FieldValue.objects.create(value="Gai", field=marque)

        field_group_temp = FieldGroup.objects.create(name="GroupeTest", is_equipment=False)
        Field.objects.create(name="Toto", field_group=field_group_temp)

    def temporary_file(self):
        """
        Returns a new temporary file
        """
        import tempfile
        tmp_file = tempfile.TemporaryFile()
        tmp_file.write(b'Coco veut un gateau')
        tmp_file.seek(0)
        return tmp_file

    def add_add_perm_file(self, user):
        """
            Add add permission for file
        """
        permission = Permission.objects.get(codename='add_file')
        user.user_permissions.add(permission)

    def add_view_perm(self, user):
        """
            Add view permission to user
        """
        perm_view = Permission.objects.get(codename="view_equipment")
        user.user_permissions.set([perm_view])

    def add_add_perm(self, user):
        """
            Add add permission to user
        """
        perm_add = Permission.objects.get(codename="add_equipment")
        user.user_permissions.add(perm_add)

    def add_change_perm(self, user):
        """
            Add change permission to user
        """
        perm_change = Permission.objects.get(codename="change_equipment")
        user.user_permissions.set([perm_change])

    def add_delete_perm(self, user):
        """
            Add delete permission to user
        """
        perm_delete = Permission.objects.get(codename="delete_equipment")
        user.user_permissions.set([perm_delete])

    def test_US4_I1_equipmentlist_get_with_perm(self):
        """
            Test if a user with perm receive the equipments' list
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        equipments = Equipment.objects.all()
        serializer = EquipmentSerializer(equipments, many=True)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/maintenancemanagement/equipments/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_US4_I1_equipmentlist_get_without_perm(self):
        """
            Test if a user without perm doesn't receive the equipments' list
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/maintenancemanagement/equipments/")
        self.assertEqual(response.status_code, 401)

    def test_US4_I2_equipmentlist_post_with_perm(self):
        """
            Test if a user with perm can add an equipment
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.post(
            "/api/maintenancemanagement/equipments/", {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Equipment.objects.get(name="Renault Kangoo"))

    def test_US4_I2_equipmentlist_post_without_perm(self):
        """
            Test if a user without perm can't add an equipment
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.post(
            "/api/maintenancemanagement/equipments/", {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id
            }
        )
        self.assertEqual(response.status_code, 401)

    def test_US4_I3_equipmentdetail_get_with_perm(self):
        """
            Test if a user with perm can receive the equipment data
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)

        equipment = Equipment.objects.get(name="Peugeot Partner")
        serializer = EquipmentDetailsSerializer(equipment)
        response = c.get("/api/maintenancemanagement/equipments/" + str(equipment.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_US4_I3_equipmentdetail_get_without_perm(self):
        """
            Test if a user without perm can't receive the equipment data
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)

        equipment = Equipment.objects.get(name="Peugeot Partner")
        response = c.get("/api/maintenancemanagement/equipments/" + str(equipment.id) + "/")
        self.assertEqual(response.status_code, 401)

    def test_US4_I4_equipmentdetail_put_with_perm(self):
        """
            Test if a user with perm can change an equipment
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_change_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Peugeot Partner")
        response = c.put(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/", {"name": "Renault Trafic"},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Equipment.objects.get(name="Renault Trafic"))

    def test_US4_I4_equipmentdetail_put_without_perm(self):
        """
            Test if a user without perm can't change an equipment
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Peugeot Partner")
        response = c.put(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/", {"name": "Renault Trafic"},
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_US4_I5_equipmentdetail_delete_with_perm(self):
        """
            Test if a user with perm can delete an equipment
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_delete_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Peugeot Partner")
        response = c.delete("/api/maintenancemanagement/equipments/" + str(equipment.id) + "/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Equipment.objects.filter(id=equipment.id).exists())

    def test_US4_I5_equipmentdetail_delete_without_perm(self):
        """
            Test if a user without perm can't delete an equipment
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Peugeot Partner")
        response = c.delete("/api/maintenancemanagement/equipments/" + str(equipment.id) + "/")
        self.assertEqual(response.status_code, 401)

    def test_US4_I8_equipmentrequirements_get_with_perm(self):
        """
            Test if a user can get equipment types requirements with permission
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/equipments/requirements')
        equipment_type = EquipmentType.objects.get(name='EquipmentTypeTest')
        field_without_value = Field.objects.get(name='FieldWithoutValueTest')
        field_with_value = Field.objects.get(name='FieldWithValueTest')
        equipment_type_requirements_json = {
            'id':
                equipment_type.id,
            'name':
                'EquipmentTypeTest',
            'field':
                [
                    {
                        'id': field_without_value.id,
                        'name': 'FieldWithoutValueTest',
                        'value': []
                    }, {
                        'id': field_with_value.id,
                        'name': 'FieldWithValueTest',
                        'value': ['FieldValueTest']
                    }
                ]
        }
        self.assertEqual(response.status_code, 200)
        self.assertTrue(equipment_type_requirements_json in response.json())

    def test_US4_I8_equipmentrequirements_get_without_perm(self):
        """
            Test if a user can get equipment types requirements without permission
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/equipments/requirements')
        self.assertEqual(response.status_code, 401)

    def test_US7_I1_equipmentlist_post_with_file_with_perm(self):
        """
            Test if a user with perm can add an equipment with a file
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm_file(user)
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        response1 = c.post("/api/maintenancemanagement/files/", data, format='multipart')
        pk = response1.data['id']
        response = c.post(
            "/api/maintenancemanagement/equipments/", {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)

    def test_US7_I1_equipmentlist_post_with_file_without_perm(self):
        """
            Test if a user without perm can't add an equipment with a file
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm_file(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        response1 = c.post("/api/maintenancemanagement/files/", data, format='multipart')
        pk = response1.data['id']
        response = c.post(
            "/api/maintenancemanagement/equipments/", {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_US7_I2_equipmentdetail_get_with_file_with_perm(self):
        """
            Test if a user with perm can receive the equipment data with a file
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        self.add_add_perm(user)
        self.add_add_perm_file(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        response1 = c.post("/api/maintenancemanagement/files/", data, format='multipart')
        pk = response1.data['id']
        c.post(
            "/api/maintenancemanagement/equipments/", {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk]
            },
            format='json'
        )
        equipment = Equipment.objects.get(name="Renault Kangoo")
        serializer = EquipmentDetailsSerializer(equipment)
        response = c.get("/api/maintenancemanagement/equipments/" + str(equipment.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_US7_I2_equipmentdetail_get_with_file_without_perm(self):
        """
            Test if a user without perm can't receive the equipment data with a file
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        self.add_add_perm_file(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        response1 = c.post("/api/maintenancemanagement/files/", data, format='multipart')
        pk = response1.data['id']
        c.post(
            "/api/maintenancemanagement/equipments/", {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk]
            },
            format='json'
        )
        equipment = Equipment.objects.get(name="Renault Kangoo")
        response = c.get("/api/maintenancemanagement/equipments/" + str(equipment.id) + "/")
        self.assertEqual(response.status_code, 401)

    def test_US7_I1_equipmentlist_post_with_files_with_perm(self):
        """
            Test if a user with perm can add an equipment with multiple files
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm_file(user)
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        data2 = {'file': self.temporary_file(), 'is_manual': 'True'}
        response1 = c.post("/api/maintenancemanagement/files/", data, format='multipart')
        response2 = c.post("/api/maintenancemanagement/files/", data2, format='multipart')
        pk_1 = response1.data['id']
        pk_2 = response2.data['id']
        response = c.post(
            "/api/maintenancemanagement/equipments/", {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk_1, pk_2]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)

    def test_US7_I1_equipmentlist_post_with_files_without_perm(self):
        """
            Test if a user without perm can't add an equipment with multiple files
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm_file(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        data2 = {'file': self.temporary_file(), 'is_manual': 'True'}
        response1 = c.post("/api/maintenancemanagement/files/", data, format='multipart')
        response2 = c.post("/api/maintenancemanagement/files/", data2, format='multipart')
        pk_1 = response1.data['id']
        pk_2 = response2.data['id']
        response = c.post(
            "/api/maintenancemanagement/equipments/", {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk_1, pk_2]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_US7_I2_equipmentdetail_get_with_files_with_perm(self):
        """
            Test if a user with perm can receive the equipment data with multiple files
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        self.add_add_perm(user)
        self.add_add_perm_file(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        data2 = {'file': self.temporary_file(), 'is_manual': 'True'}
        response1 = c.post("/api/maintenancemanagement/files/", data, format='multipart')
        response2 = c.post("/api/maintenancemanagement/files/", data2, format='multipart')
        pk_1 = response1.data['id']
        pk_2 = response2.data['id']
        c.post(
            "/api/maintenancemanagement/equipments/", {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk_1, pk_2]
            },
            format='json'
        )
        equipment = Equipment.objects.get(name="Renault Kangoo")
        serializer = EquipmentDetailsSerializer(equipment)
        response = c.get("/api/maintenancemanagement/equipments/" + str(equipment.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_US7_I2_equipmentdetail_get_with_files_without_perm(self):
        """
            Test if a user without perm can't receive the equipment data with multiple files
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        self.add_add_perm_file(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        data2 = {'file': self.temporary_file(), 'is_manual': 'True'}
        response1 = c.post("/api/maintenancemanagement/files/", data, format='multipart')
        pk_1 = response1.data['id']
        response2 = c.post("/api/maintenancemanagement/files/", data2, format='multipart')
        pk_2 = response2.data['id']
        c.post(
            "/api/maintenancemanagement/equipments/", {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk_1, pk_2]
            },
            format='json'
        )
        equipment = Equipment.objects.get(name="Renault Kangoo")
        response = c.get("/api/maintenancemanagement/equipments/" + str(equipment.id) + "/")
        self.assertEqual(response.status_code, 401)

    def test_US21_I1_equipmentlist_post_with_all_fields_with_perm(self):
        """
            Test if a user with perm can add an equipment with fields from equipment type
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm_file(user)
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.post(
            "/api/maintenancemanagement/equipments/", {
                "name":
                    "Embouteilleuse AXB1",
                "equipment_type":
                    EquipmentType.objects.get(name="embouteilleuse").id,
                "field":
                    [
                        {
                            "field": Field.objects.get(name="Capacité").id,
                            "value": "60000",
                            "description": "Nb de bouteilles par h"
                        }, {
                            "field": Field.objects.get(name="Pression Normale").id,
                            "value": "5 bars"
                        }, {
                            "field": Field.objects.get(name="marque").id,
                            "value": "Gai"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)

    def test_US21_I1_equipmentlist_post_with_missing_fields_with_perm(self):
        """
            Test if a user with perm can add an equipment with some missing fields
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm_file(user)
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.post(
            "/api/maintenancemanagement/equipments/", {
                "name":
                    "Embouteilleuse AXB1",
                "equipment_type":
                    EquipmentType.objects.get(name="embouteilleuse").id,
                "field":
                    [
                        {
                            "field": Field.objects.get(name="Capacité").id,
                            "value": "60000",
                            "description": "Nb de bouteilles par h"
                        }, {
                            "field": Field.objects.get(name="marque").id,
                            "value": "Gai"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_US21_I1_equipmentlist_post_without_value_with_perm(self):
        """
            Test if a user with perm can add an equipment with some bad fields
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm_file(user)
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.post(
            "/api/maintenancemanagement/equipments/", {
                "name":
                    "Embouteilleuse AXB1",
                "equipment_type":
                    EquipmentType.objects.get(name="embouteilleuse").id,
                "fields":
                    [
                        {
                            "field": Field.objects.get(name="Capacité").id,
                            "value": "60000",
                            "description": "Nb de bouteilles par h"
                        }, {
                            "field": Field.objects.get(name="Pression Normale").id
                        }, {
                            "field": Field.objects.get(name="marque").id,
                            "value": "Gai"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_US21_I1_equipmentlist_post_with_bad_field_value_with_perm(self):
        """
            Test if a user with perm can add an equipment with some bad fields
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm_file(user)
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.post(
            "/api/maintenancemanagement/equipments/", {
                "name":
                    "Embouteilleuse AXB1",
                "equipment_type":
                    EquipmentType.objects.get(name="embouteilleuse").id,
                "fields":
                    [
                        {
                            "field": Field.objects.get(name="Capacité").id,
                            "value": "60000",
                            "description": "Nb de bouteilles par h"
                        }, {
                            "field": Field.objects.get(name="Pression Normale").id,
                            "value": "5 bars"
                        }, {
                            "field": Field.objects.get(name="marque").id,
                            "value": "WRONG_FIELD_VALUE"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_US21_I1_equipmentlist_post_with_extra_fields_with_perm(self):
        """
            Test if a user with perm can add an equipment with fields from equipment type
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm_file(user)
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.post(
            "/api/maintenancemanagement/equipments/", {
                "name":
                    "Embouteilleuse AXB1",
                "equipment_type":
                    EquipmentType.objects.get(name="embouteilleuse").id,
                "field":
                    [
                        {
                            "field": Field.objects.get(name="Capacité").id,
                            "name": "Capacité",
                            "value": "60000",
                            "description": "Nb de bouteilles par h"
                        }, {
                            "field": Field.objects.get(name="Pression Normale").id,
                            "value": "5 bars",
                            "name": "Pression Normale"
                        }, {
                            "field": Field.objects.get(name="marque").id,
                            "value": "Gai",
                            "name": "marque"
                        }, {
                            "field": Field.objects.get(name="Toto").id,
                            "value": "EXTRA_FIELD",
                            "name": "Toto"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)

    def test_US21_I2_equipmentdetails_put_with_all_fields_with_perm(self):
        """
            Test if a user with perm can update an equipment with fields from equipment type
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_change_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Embouteilleuse AXB1")
        capacite = Field.objects.get(name="Nb bouteilles")
        pression = Field.objects.get(name="Pression")
        marque = Field.objects.get(name="Marque")
        response = c.put(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/", {
                "name":
                    "Embouteilleuse AXB7",
                "equipment_type":
                    EquipmentType.objects.get(name="Embouteilleuse").id,
                "field":
                    [
                        {
                            "id": FieldObject.objects.get(field=capacite).id,
                            "field": capacite.id,
                            "value": "80000",
                            "description": "Nb de bouteilles par h"
                        }, {
                            "id": FieldObject.objects.get(field=pression).id,
                            "field": pression.id,
                            "value": "3 bars"
                        }, {
                            "id": FieldObject.objects.get(field=marque).id,
                            "field": marque.id,
                            "field_value":
                                {
                                    "id": FieldValue.objects.get(value="BOSH").id,
                                    "value": "BOSH",
                                    "field": marque.id
                                }
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        equipment = Equipment.objects.get(name="Embouteilleuse AXB7")
        serializer = EquipmentDetailsSerializer(equipment)
        self.assertEqual(serializer.data, response.json())

    def test_US21_I2_equipmentdetails_put_without_perm(self):
        """
            Test if a user without perm can't update an equipment with fields from equipment type
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Embouteilleuse AXB1")
        capacite = Field.objects.get(name="Nb bouteilles")
        pression = Field.objects.get(name="Pression")
        marque = Field.objects.get(name="Marque")
        response = c.put(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/", {
                "name":
                    "Embouteilleuse AXB7",
                "equipment_type":
                    EquipmentType.objects.get(name="Embouteilleuse").id,
                "field":
                    [
                        {
                            "id": FieldObject.objects.get(field=capacite).id,
                            "field": capacite.id,
                            "value": "80000",
                            "description": "Nb de bouteilles par h"
                        }, {
                            "id": FieldObject.objects.get(field=pression).id,
                            "field": pression.id,
                            "value": "3 bars"
                        }, {
                            "id": FieldObject.objects.get(field=marque).id,
                            "field": marque.id,
                            "field_value":
                                {
                                    "id": FieldValue.objects.get(value="BOSH").id,
                                    "value": "BOSH",
                                    "field": marque.id
                                }
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_US21_I2_equipmentdetails_put_with_some_fields_with_perm(self):
        """
            Test if a user with perm can update an equipment with fields from equipment type
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_change_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Embouteilleuse AXB1")
        capacite = Field.objects.get(name="Nb bouteilles")
        pression = Field.objects.get(name="Pression")
        marque = Field.objects.get(name="Marque")
        response = c.put(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/", {
                "name":
                    "Embouteilleuse AXB7",
                "equipment_type":
                    EquipmentType.objects.get(name="Embouteilleuse").id,
                "field":
                    [
                        {
                            "id": FieldObject.objects.get(field=capacite).id,
                            "field": capacite.id,
                            "value": "80000",
                            "description": "Nb de bouteilles par h"
                        }, {
                            "id": FieldObject.objects.get(field=pression).id,
                            "field": pression.id,
                            "value": "3 bars"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        equipment = Equipment.objects.get(name="Embouteilleuse AXB7")
        serializer = EquipmentDetailsSerializer(equipment)
        self.assertEqual(serializer.data, response.json())

    def test_US21_I2_equipmentdetails_put_with_wrong_fieldvalues_with_perm(self):
        """
            Test if a user with perm can update an equipment with fields from equipment type
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_change_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Embouteilleuse AXB1")
        capacite = Field.objects.get(name="Nb bouteilles")
        pression = Field.objects.get(name="Pression")
        marque = Field.objects.get(name="Marque")
        response = c.put(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/", {
                "name":
                    "Embouteilleuse AXB7",
                "equipment_type":
                    EquipmentType.objects.get(name="Embouteilleuse").id,
                "field":
                    [
                        {
                            "id": FieldObject.objects.get(field=capacite).id,
                            "field": capacite.id,
                            "value": "80000",
                            "description": "Nb de bouteilles par h"
                        }, {
                            "id": FieldObject.objects.get(field=pression).id,
                            "field": pression.id,
                            "value": "3 bars"
                        }, {
                            "id": FieldObject.objects.get(field=marque).id,
                            "field": marque.id,
                            "field_value": {
                                "id": -1,
                                "value": "Audi",
                                "field": marque.id
                            }
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_US21_I2_equipmentdetails_put_with_new_fields_with_perm(self):
        """
            Test if a user with perm can update an equipment with fields from equipment type
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_change_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Embouteilleuse AXB1")
        pression = Field.objects.get(name="Pression")
        marque = Field.objects.get(name="Marque")
        response = c.put(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/", {
                "name":
                    "Embouteilleuse AXB7",
                "equipment_type":
                    EquipmentType.objects.get(name="Embouteilleuse").id,
                "field":
                    [
                        {
                            "id": FieldObject.objects.get(field=pression).id,
                            "field": pression.id,
                            "value": "3 bars"
                        }, {
                            "id": FieldObject.objects.get(field=marque).id,
                            "field": marque.id,
                            "field_value":
                                {
                                    "id": FieldValue.objects.get(value="BOSH").id,
                                    "value": "BOSH",
                                    "field": marque.id
                                }
                        }, {
                            "name": "NewField",
                            "value": "42",
                            "description": "Il s'agit d'un nouveau Field"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        equipment = Equipment.objects.get(name="Embouteilleuse AXB7")
        serializer = EquipmentDetailsSerializer(equipment)
        self.assertEqual(serializer.data, response.json())

    def test_US21_I2_equipmentdetails_put_with_wrong_new_fields_with_perm(self):
        """
            Test if a user with perm can update an equipment with fields from equipment type
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_change_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Embouteilleuse AXB1")
        pression = Field.objects.get(name="Pression")
        marque = Field.objects.get(name="Marque")
        response = c.put(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/", {
                "name":
                    "Equipement avec nouveau type",
                "equipment_type":
                    EquipmentType.objects.get(name="Embouteilleuse").id,
                "field":
                    [
                        {
                            "id": FieldObject.objects.get(field=pression).id,
                            "field": pression.id,
                            "value": "3 bars"
                        }, {
                            "id": FieldObject.objects.get(field=marque).id,
                            "field": marque.id,
                            "field_value":
                                {
                                    "id": FieldValue.objects.get(value="BOSH").id,
                                    "value": "BOSH",
                                    "field": marque.id
                                }
                        }, {
                            "value": "3",
                            "description": "WRONG NEW FIELD"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_US21_I2_equipmentdetails_put_with_new_equipmenttype_with_perm(self):
        """
            Test if a user with perm can update an equipment with a new equipment type
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_change_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Embouteilleuse AXB1")
        response = c.put(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/", {
                "name":
                    "Embouteilleuse AXB7",
                "equipment_type":
                    EquipmentType.objects.get(name="EquipmentTypeTest").id,
                "field":
                    [
                        {
                            "field": Field.objects.get(name="FieldWithoutValueTest").id,
                            "value": "13",
                            "description": "Simple field"
                        }, {
                            "field": Field.objects.get(name="FieldWithValueTest").id,
                            "value": "FieldValueTest"
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        equipment = Equipment.objects.get(name="Embouteilleuse AXB7")
        serializer = EquipmentDetailsSerializer(equipment)
        self.assertEqual(serializer.data, response.json())
