from maintenancemanagement.models import (
    Equipment,
    EquipmentType,
    Field,
    FieldGroup,
    FieldValue,
)
from maintenancemanagement.serializers import (
    EquipmentTypeDetailsSerializer,
    EquipmentTypeSerializer,
)
from openCMMS import settings
from usersmanagement.models import UserProfile

from django.contrib.auth.models import Permission
from django.test import TestCase
from rest_framework.test import APIClient

User = settings.AUTH_USER_MODEL

#note à la personne faisant passer les tests : il faudra sûrement changer les imports et checker les URL


class EquipmentTypeTests(TestCase):

    def set_up_perm(self):
        """
            Set up a user with permissions
        """
        permission = Permission.objects.get(codename='add_equipmenttype')
        permission2 = Permission.objects.get(codename='view_equipmenttype')
        permission3 = Permission.objects.get(codename='delete_equipmenttype')
        permission4 = Permission.objects.get(codename='change_equipmenttype')
        user = UserProfile.objects.create(username='tom')
        user.set_password('truc')
        user.first_name = 'Tom'
        user.save()
        user.user_permissions.add(permission)
        user.user_permissions.add(permission2)
        user.user_permissions.add(permission3)
        user.user_permissions.add(permission4)
        user.save()
        return user

    def set_up_without_perm(self):
        """
            Set up a user without permissions
        """
        user = UserProfile.objects.create(username='tom')
        user.set_password('truc')
        user.first_name = 'Tom'
        user.save()
        return user

    def test_US4_I9_equipmenttypelist_get_with_perm(self):
        """
        Test if a user with perm can retrieve all the equipmenttypes

                Inputs:
                    user (UserProfile): A UserProfile we create with the required permissions.

                Expected outputs:
                    We expect a response data which match what we expect
        """
        self.set_up_perm()
        equipment_type = EquipmentType.objects.all()
        serializer = EquipmentTypeSerializer(equipment_type, many=True)
        client = APIClient()
        user = UserProfile.objects.get(username='tom')
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/equipmenttypes/', format='json')
        self.assertEqual(serializer.data, response.json())

    def test_US4_I9_equipmenttypelist_get_without_perm(self):
        """
        Test if a user with perm can't retrieve all the equipmenttypes

                Inputs:
                    user (UserProfile): A UserProfile we create without the required permissions.

                Expected outputs:
                    We expect a 401 status code in the response
        """
        self.set_up_without_perm()
        client = APIClient()
        user = UserProfile.objects.get(username='tom')
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/equipmenttypes/', format='json')
        self.assertEqual(response.status_code, 401)

    def test_US4_I10_equipmenttypelist_post_with_perm(self):
        """
        Test if a user with perm can add an equipmenttype

                Inputs:
                    user (UserProfile): A UserProfile we create with the required permissions.
                    data (json): A dictionnary with all the required information to create an equipmenttype

                Expected outputs:
                    We expect a 201 status code in the response
        """
        self.set_up_perm()
        client = APIClient()
        user = UserProfile.objects.get(username='tom')
        client.force_authenticate(user=user)
        response = client.post(
            '/api/maintenancemanagement/equipmenttypes/', {
                'name': 'car',
                'equipment_set': []
            }, format='json'
        )
        self.assertEqual(response.status_code, 201)

    def test_US4_I10_equipmenttypelist_post_without_perm(self):
        """
        Test if a user without perm can add an equipmenttype

                Inputs:
                    user (UserProfile): A UserProfile we create without the required permissions.
                    data (json): A dictionnary with all the required information to create an equipmenttype

                Expected outputs:
                    We expect a 401 status code in the response
        """
        self.set_up_without_perm()
        client = APIClient()
        user = UserProfile.objects.get(username='tom')
        client.force_authenticate(user=user)
        response = client.post('/api/maintenancemanagement/equipmenttypes/', {'name': 'tool'}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_US4_I11_equipmenttypedetail_get_with_perm(self):
        """
        Test if a user with perm can retrieve an equipmenttype details

                Inputs:
                    user (UserProfile): A UserProfile we create with the required permissions.

                Expected outputs:
                    We expect a 200 status code in the response
                    We expect a response data which match what we expect

        """
        self.set_up_perm()
        tool = EquipmentType.objects.create(name="tool")
        serializer = EquipmentTypeDetailsSerializer(tool)
        client = APIClient()
        user = UserProfile.objects.get(username='tom')
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/equipmenttypes/' + str(tool.id) + "/", format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_US4_I11_equipmenttypedetail_get_without_perm(self):
        """
        Test if a user without perm can retrieve an equipmenttype

                Inputs:
                    user (UserProfile): A UserProfile we create without the required permissions.

                Expected outputs:
                    We expect a 401 status code in the response
        """
        self.set_up_without_perm()
        tool = EquipmentType.objects.create(name="tool")
        serializer = EquipmentTypeSerializer(tool)
        client = APIClient()
        user = UserProfile.objects.get(username='tom')
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/equipmenttypes/' + str(tool.id) + "/", format='json')
        self.assertEqual(response.status_code, 401)

    def test_US4_I12_equipmenttypedetail_put_with_perm(self):
        """
        Test if a user with perm can update an equipmenttype

                Inputs:
                    user (UserProfile): A UserProfile we create with the required permissions.
                    data (json): A dictionnary with all the required information to update an equipmenttype

                Expected outputs:
                    We expect a 200 status code in the response
                    We expect that the information we changed is updated in the database
        """
        self.set_up_perm()
        tool = EquipmentType.objects.create(name="tool")
        client = APIClient()
        user = UserProfile.objects.get(username='tom')
        client.force_authenticate(user=user)
        response = client.put(
            '/api/maintenancemanagement/equipmenttypes/' + str(tool.id) + '/', {"name": "car"}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(EquipmentType.objects.get(name="car"))

    def test_US4_I12_equipmenttypedetail_put_without_perm(self):
        """
        Test if a user without perm can update an equipmenttype

                Inputs:
                    user (UserProfile): A UserProfile we create without the required permissions.
                    data (json): A dictionnary with all the required information to update an equipmenttype

                Expected outputs:
                    We expect a 401 status code in the response
        """
        self.set_up_without_perm()
        tool = EquipmentType.objects.create(name="tool")
        client = APIClient()
        user = UserProfile.objects.get(username='tom')
        client.force_authenticate(user=user)
        response = client.put(
            '/api/maintenancemanagement/equipmenttypes/' + str(tool.id) + '/', {"name": "car"}, format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_US4_I13_equipmenttypedetail_delete_with_perm(self):
        """
        Test if a user with perm can delete an equipmenttype 

                Inputs:
                    user (UserProfile): A UserProfile we create with the required permissions.

                Expected outputs:
                    We expect a 204 status code in the response
                    We expect that the equipmenttype we deleted is no longer in the database

        """
        self.set_up_perm()
        user = UserProfile.objects.get(username="tom")
        client = APIClient()
        client.force_authenticate(user=user)
        tool = EquipmentType.objects.create(name="tool")
        response_1 = client.get('/api/maintenancemanagement/equipmenttypes/' + str(tool.id) + '/', format='json')
        response_2 = client.delete('/api/maintenancemanagement/equipmenttypes/' + str(tool.id) + '/')
        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(response_2.status_code, 204)
        self.assertFalse(EquipmentType.objects.filter(id=tool.id).exists())

    def test_US4_I13_equipmenttypedetail_delete_without_perm(self):
        """
        Test if a user without perm can delete an equipmenttype

                Inputs:
                    user (UserProfile): A UserProfile we create without the required permissions.

                Expected outputs:
                    We expect a 401 status code in the response
        """
        self.set_up_without_perm()
        user = UserProfile.objects.get(username="tom")
        client = APIClient()
        client.force_authenticate(user=user)
        tool = EquipmentType.objects.create(name="tool")
        response = client.delete('/api/maintenancemanagement/equipmenttypes/' + str(tool.id) + '/')
        self.assertEqual(response.status_code, 401)

    def test_US20_I1_equipmenttypelist_post_with_fields_with_perm(self):
        """
        Test if a user with perm can add an equipmenttype with field

                Inputs:
                    user (UserProfile): A UserProfile we create with the required permissions.
                    data (json): A dictionnary with all the required information to create an equipmenttype with fields

                Expected outputs:
                    We expect a 201 status code in the response
                    We expect that the fields we created are all in the database with the correct values
        """
        self.set_up_perm()
        client = APIClient()
        user = UserProfile.objects.get(username='tom')
        client.force_authenticate(user=user)
        response = client.post(
            '/api/maintenancemanagement/equipmenttypes/', {
                'name':
                    'car',
                'equipment_set': [],
                'field':
                    [
                        {
                            "name": "test_add_equipmenttype_with_perm_with_fields_1"
                        }, {
                            "name": "test_add_equipmenttype_with_perm_with_fields_2",
                            "value": ["Renault", "Volvo", "BMW"]
                        }
                    ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        equipment_type = EquipmentType.objects.get(name="car")
        field_group = FieldGroup.objects.get(name="car")
        field_1 = Field.objects.get(name="test_add_equipmenttype_with_perm_with_fields_1")
        field_2 = Field.objects.get(name="test_add_equipmenttype_with_perm_with_fields_2")
        field_value_1 = FieldValue.objects.get(value="Renault")
        field_value_2 = FieldValue.objects.get(value="Volvo")
        field_value_3 = FieldValue.objects.get(value="BMW")
        self.assertEqual(field_1.field_group, field_group)
        self.assertEqual(field_2.field_group, field_group)
        self.assertTrue(equipment_type in field_group.equipmentType_set.all())
        self.assertEqual(field_value_1.field, field_2)
        self.assertEqual(field_value_2.field, field_2)
        self.assertEqual(field_value_3.field, field_2)
