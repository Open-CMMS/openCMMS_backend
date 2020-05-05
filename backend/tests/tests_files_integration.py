from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission 
from django.test import TestCase, Client
from rest_framework.test import APIClient
from usersmanagement.models import UserProfile
from maintenancemanagement.models import File
from maintenancemanagement.serializers import FileSerializer

class FileTests(TestCase):

    def set_up_perm(self):
        """
            Set up a user with permissions
        """
        permission = Permission.objects.get(codename='add_file')
        permission2 = Permission.objects.get(codename='view_file')  
        permission3 = Permission.objects.get(codename='delete_file')
        permission4 = Permission.objects.get(codename='change_file')                             
        
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
    
    def temporary_file(self):
        """
        Returns a new temporary file
        """
        import tempfile
        tmp_file = tempfile.TemporaryFile()
        tmp_file.write('Coco veut un gateau')
        tmp_file.seek(0)
        return tmp_file
    
    def test_can_acces_files_list_with_perm(self):
        """
            Test if a user with perm receive the data
        """
        user = self.set_up_perm()
        file = File.objects.all()
        serializer = FileSerializer(file, many=True)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/files/', format='json')
        self.assertEqual(response.data,serializer.data)

    def test_can_acces_file_list_without_perm(self):
        """
            Test if a user without perm doesn't receive the data
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/files/', format='json')
        self.assertEqual(response.status_code,401)

    def test_add_file_with_perm(self):
        """
            Test if a user with perm can add a file.
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {
            'file': self.temporary_file(),
            'is_manual': 'False'
        }
        response = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        self.assertEqual(response.status_code, 201)
    
    def test_add_file_without_perm(self):
        """
            Test if a user without perm can't add a file.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/maintenancemanagement/files/', format='multipart')
        self.assertEqual(response.status_code,401)

    def test_view_file_request_with_perm(self):
        """
            Test if a user with perm can see a file.
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {
            'file': self.temporary_file(),
            'is_manual': 'False'
        }
        response1 = client.post('/api/maintenancemanagement/files/', data, format='multipart')
        pk = response1.data['id']
        response = client.get('/api/maintenancemanagement/files/'+str(pk)+'/')
        file = open(response.data["file"])
        self.assertEqual(file.read(), "Coco veut un gateau")
    
    def test_view_task_request_without_perm(self):
        """
            Test if a user without perm can't see a file detail
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {
            'file': self.temporary_file(),
            'is_manual': 'False'
        }
        response1 = client.post('/api/maintenancemanagement/files/', data, format='multipart')
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/files/'+str(pk)+'/')
        self.assertEqual(response.status_code,401)
    
    def test_delete_file_with_perm(self):
        """
            Test if a user with perm can delete a file
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {
            'file': self.temporary_file(),
            'is_manual': 'False'
        }
        response1 = client.post('/api/maintenancemanagement/files/', data, format='multipart')
        pk = response1.data['id']
        response = client.delete('/api/maintenancemanagement/files/'+str(pk)+'/')
        self.assertEqual(response.status_code, 204)
    
    def test_delete_file_without_perm(self):
        """
            Test if a user without perm can delete a file
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {
            'file': self.temporary_file(),
            'is_manual': 'False'
        }
        response1 = client.post('/api/maintenancemanagement/files/', data, format='multipart')
        pk = response1.data['id']
        user.user_permissions.clear()
        user = UserProfile.objects.get(id=user.pk)
        client.force_authenticate(user=user)
        response = client.delete('/api/maintenancemanagement/files/'+str(pk)+'/')
        self.assertEqual(response.status_code, 401)