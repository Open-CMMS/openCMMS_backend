from django.urls import reverse
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.contrib.auth.models import Permission
from maintenancemanagement.models import EquipmentType
from rest_framework.test import APIClient
from maintenancemanagement.views.views_equipment_type import *
from django.contrib.contenttypes.models import ContentType

#note à la personne faisant passer les tests : il faudra sûrement changer les imports et checker les URL

class EquipmentTypeTests(TestCase):

    def set_up_perm(self):
        """
            Set up a user with permissions
        """
        content_type = ContentType.objects.get_for_model(EquipmentType)
        permission = Permission.objects.create(codename='add_equipmenttype',
                                       name='Can add an equipment type',
                                       content_type=content_type)
        permission2 = Permission.objects.create(codename='view_equipmenttype',
                                       name='Can view an equipment type',
                                       content_type=content_type)
        permission3 = Permission.objects.create(codename='delete_equipmenttype',
                                       name='Can delete an equipment type',
                                       content_type=content_type)
        permission4 = Permission.objects.create(codename='change_equipmenttype',
                                       name='Can update an equipment type',
                                       content_type=content_type)
        user = UserProfile.objects.create(username='tom')
        user.set_password('truc')
        user.first_name='Tom'
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
        user.first_name='Tom'
        user.save()
        return user

    def test_can_access_equipmenttype_list_with_perm(self):
        """
            Test if a user with perm receive the data
        """
        self.set_up_perm()
        equipment_type = EquipmentType.objects.all()
        serializer = EquipmentTypeSerializer(equipment_type, many=True)
        client = APIClient()
        client.login(username='tom', password='truc')
        response = client.get('/api/maintenancemanagement/equipmenttypes/', format='json')
        self.assertEqual(response.data, serializer.data)

    def test_can_access_equipmenttype_list_without_perm(self):
        """
            Test if a user without perm doesn't receive the data
        """
        self.set_up_without_perm()
        client = APIClient()
        client.login(username='tom', password='truc')
        response = client.get('/api/maintenancemanagement/equipmenttypes/', format='json')
        self.assertEqual(response.status_code,401)

    def test_add_equipmenttype_with_perm(self):
        """
            Test if a user with perm can add an equipment type
        """
        self.set_up_perm()
        client = APIClient()
        client.login(username='tom', password='truc')
        response = client.post('/api/maintenancemanagement/equipmenttypes/', {'name': 'car'}, format='json')
        self.assertEqual(response.status_code,201)

    def test_add_equipmenttype_without_perm(self):
        """
            Test if a user without perm can't add an equipment type
        """
        self.set_up_without_perm()
        client = APIClient()
        client.login(username='tom', password='truc')
        response = client.post('/api/maintenancemanagement/equipmenttypes/', {'name': 'tool'}, format='json')
        self.assertEqual(response.status_code,401)

    def test_view_equipmenttype_request_with_perm(self):
        """
            Test if a user with perm can see an equipment type detail
        """
        user = self.set_up_perm()
        EquipmentType(name = 'tool')
        client = APIClient()
        client.login(username='tom', password='truc')
        response1 = client.post('/api/maintenancemanagement/equipmenttypes/', {'name': 'tool'}, format='json')
        pk = response1.data['id']
        response = client.get('/api/maintenancemanagement/equipmenttypes/'+str(pk)+'/')
        self.assertEqual(response.data['name'],'tool')

    def test_view_equipmenttype_request_without_perm(self):
        """
            Test if a user without perm can't see
        """
        user = self.set_up_perm()
        EquipmentType(name = 'tool')
        client = APIClient()
        client.login(username='tom', password='truc')
        response1 = client.post('/api/maintenancemanagement/equipmenttypes/', {'name': 'tool'}, format='json')
        pk = response1.data['id']
        user.user_permissions.clear()
        response = client.get('/api/maintenancemanagement/equipmenttypes/'+str(pk)+'/')
        self.assertEqual(response.status_code,401)


    def test_view_equipmenttype_request_with_perm(self):
        """
            Test if a user with perm can change an equipment type detail
        """
        user = self.set_up_perm()
        EquipmentType(name = 'tool')
        client = APIClient()
        client.login(username='tom', password='truc')
        response1 = client.post('/api/maintenancemanagement/equipmenttypes/', {'name': 'tool'}, format='json')
        pk = response1.data['id']
        response = client.put('/api/maintenancemanagement/equipmenttypes/'+str(pk)+'/', {'name': 'car'}, format='json')
        self.assertEqual(response.data['name'],'car')

    def test_view_equipmenttype_request_without_perm(self):
        """
            Test if a user without perm can't change an equipment type detail
        """
        user = self.set_up_perm()
        EquipmentType(name = 'tool')
        client = APIClient()
        client.login(username='tom', password='truc')
        response1 = client.post('/api/maintenancemanagement/equipmenttypes/', {'name': 'tool'}, format='json')
        pk = response1.data['id']
        user.user_permissions.clear()
        response = client.put('/api/maintenancemanagement/equipmenttypes/'+str(pk)+'/', {'name':'car'}, format='json')
        self.assertEqual(response.status_code,401)


    def test_delete_equipmenttype_request_with_perm(self):
        """
            Test if a user with perm can delete an equipment type
        """
        user = self.set_up_perm()
        EquipmentType(name = 'tool')
        client = APIClient()
        client.login(username='tom', password='truc')
        response1 = client.post('/api/maintenancemanagement/equipmenttypes/', {'name': 'tool'}, format='json')
        pk = response1.data['id']
        response = client.delete('/api/maintenancemanagement/equipmenttypes/'+str(pk)+'/')
        self.assertEqual(response.status_code, 204)

    def test_delete_equipmenttype_request_without_perm(self):
        """
            Test if a user without perm can't deletean equipment type
        """
        user = self.set_up_perm()
        EquipmentType(name = 'tool')
        client = APIClient()
        client.login(username='tom', password='truc')
        response1 = client.post('/api/maintenancemanagement/equipmenttypes/', {'name': 'tool'}, format='json')
        pk = response1.data['id']
        user.user_permissions.clear()
        response = client.delete('/api/maintenancemanagement/equipmenttypes/'+str(pk)+'/')
        self.assertEqual(response.status_code,401)
