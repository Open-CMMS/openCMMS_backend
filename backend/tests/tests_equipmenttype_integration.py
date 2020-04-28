from django.test import TestCase
from django.contrib.auth.models import Permission
from maintenancemanagement.models import EquipmentType
from maintenancemanagement.serializers import EquipmentTypeSerializer
from usersmanagement.models import UserProfile
from rest_framework.test import APIClient
from openCMMS import settings

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
        user = UserProfile.objects.get(username='tom')
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/equipmenttype/', format='json')
        self.assertEqual(serializer.data, response.json())

    def test_can_access_equipmenttype_list_without_perm(self):
        """
            Test if a user without perm doesn't receive the data
        """
        self.set_up_without_perm()
        client = APIClient()
        user = UserProfile.objects.get(username='tom')
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/equipmenttype/', format='json')
        self.assertEqual(response.status_code,401)

    def test_add_equipmenttype_with_perm(self):
        """
            Test if a user with perm can add an equipment type
        """
        self.set_up_perm()
        client = APIClient()
        user = UserProfile.objects.get(username='tom')
        client.force_authenticate(user=user)
        response = client.post('/api/maintenancemanagement/equipmenttype/', {'name': 'car'}, format='json')
        self.assertEqual(response.status_code,201)

    def test_add_equipmenttype_without_perm(self):
        """
            Test if a user without perm can't add an equipment type
        """
        self.set_up_without_perm()
        client = APIClient()
        user = UserProfile.objects.get(username='tom')
        client.force_authenticate(user=user)
        response = client.post('/api/maintenancemanagement/equipmenttype/', {'name': 'tool'}, format='json')
        self.assertEqual(response.status_code,401)

    def test_view_equipmenttype_request_with_perm(self):
        """
            Test if a user with perm can see an equipment type detail
        """
        self.set_up_perm()
        tool = EquipmentType.objects.create(name="tool")
        serializer = EquipmentTypeSerializer(tool, many=True)
        print(tool.id)
        client = APIClient()
        user = UserProfile.objects.get(username='tom')
        client.force_authenticate(user=user)
        response = client.get("/api/maintenancemanagement/equipmenttype/", format='json')
        self.assertEqual(response.status_code,200)
        self.assertEqual(serializer.data, response.json())

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


    # def test_change_equipmenttype_request_with_perm(self):
    #     """
    #         Test if a user with perm can change an equipment type detail
    #     """
    #     self.set_up_perm()
    #     tool = EquipmentType.objects.create(name="tool")
    #     client = APIClient()
    #     user = UserProfile.objects.get(username='tom')
    #     client.force_authenticate(user=user)
    #     print(EquipmentType.objects.get(name="tool").name)
    #     response = client.get('/api/maintenancemanagement/equipmenttype/'+str(tool.id)+'/',format='json')
    #     print(response.data)
    #     self.assertEqual(response.status_code,200)
    #     self.assertTrue(EquipmentType.objects.get(name="car"))
    #
    # def test_change_equipmenttype_request_without_perm(self):
    #     """
    #         Test if a user without perm can't change an equipment type detail
    #     """
    #     user = self.set_up_perm()
    #     EquipmentType(name = 'tool')
    #     client = APIClient()
    #     client.login(username='tom', password='truc')
    #     response1 = client.post('/api/maintenancemanagement/equipmenttypes/', {'name': 'tool'}, format='json')
    #     pk = response1.data['id']
    #     user.user_permissions.clear()
    #     response = client.put('/api/maintenancemanagement/equipmenttypes/'+str(pk)+'/', {'name':'car'}, format='json')
    #     self.assertEqual(response.status_code,401)


    # def test_delete_equipmenttype_request_with_perm(self):
    #     """
    #         Test if a user with perm can delete an equipment type
    #     """
    #     user = self.set_up_perm()
    #     tool = Eq
    #     client = APIClient()
    #     client.login(username='tom', password='truc')
    #     response1 = client.post('/api/maintenancemanagement/equipmenttypes/', {'name': 'tool'}, format='json')
    #     pk = response1.data['id']
    #     response = client.delete('/api/maintenancemanagement/equipmenttypes/'+str(pk)+'/')
    #     self.assertEqual(response.status_code, 204)
    #
    # def test_delete_equipmenttype_request_without_perm(self):
    #     """
    #         Test if a user without perm can't deletean equipment type
    #     """
    #     user = self.set_up_perm()
    #     EquipmentType(name = 'tool')
    #     client = APIClient()
    #     client.login(username='tom', password='truc')
    #     response1 = client.post('/api/maintenancemanagement/equipmenttypes/', {'name': 'tool'}, format='json')
    #     pk = response1.data['id']
    #     user.user_permissions.clear()
    #     response = client.delete('/api/maintenancemanagement/equipmenttypes/'+str(pk)+'/')
    #     self.assertEqual(response.status_code,401)
