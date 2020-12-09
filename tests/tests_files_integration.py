from io import BytesIO

from PIL import Image

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from maintenancemanagement.models import File
from maintenancemanagement.serializers import FileSerializer
from openCMMS import settings
from rest_framework.test import APIClient
from usersmanagement.models import UserProfile


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

    def temporary_image(self, ext):
        """
        Returns a new temporary image.
        """
        file_obj = BytesIO()
        image = Image.new('1', (60, 60), 1)
        image.save(file_obj, ext)
        file_obj.seek(0)
        return file_obj

    def temporary_file(self):
        """
        Returns a new temporary file
        """
        import tempfile
        tmp_file = tempfile.TemporaryFile()
        tmp_file.write(b'Coco veut un gateau')
        tmp_file.seek(0)
        return tmp_file

    def test_can_acces_files_list_with_connected(self):
        """
            Test if a user with perm receive the data
        """
        user = self.set_up_without_perm()
        file = File.objects.all()
        serializer = FileSerializer(file, many=True)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/files/', format='json')
        self.assertEqual(response.data, serializer.data)

    def test_can_acces_file_list_without_connected(self):
        """
            Test if a user without perm doesn't receive the data
        """
        user = self.set_up_without_perm()
        client = APIClient()
        response = client.get('/api/maintenancemanagement/files/', format='json')
        self.assertEqual(response.status_code, 401)

    def test_add_png_file_with_connected(self):
        """
            Test if a user with perm can add a png file.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_image('png'), 'is_manual': 'False'}
        response = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_add_jpg_file_with_connected(self):
        """
            Test if a user with perm can add a jpg file.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_image('JPEG'), 'is_manual': 'False'}
        response = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_add_bitmap_file_with_connected(self):
        """
            Test if a user with perm can add a file.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_image('BMP'), 'is_manual': 'False'}
        response = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_add_pdf_file_with_connected(self):
        """
            Test if a user with perm can add a file.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_image('PDF'), 'is_manual': 'False'}
        response = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        print(response.data)
        self.assertEqual(response.status_code, 201)

    def test_add_text_file_with_connected(self):
        """
            Test if a user can't add text file.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_file(), 'is_manual': 'False'}
        response = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_add_file_without_connected(self):
        """
            Test if a user without perm can't add a file.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        response = client.post('/api/maintenancemanagement/files/', format='multipart')
        self.assertEqual(response.status_code, 401)

    def test_view_file_details_with_connected(self):
        """
            Test if a user with perm can see a file.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_image('png'), 'is_manual': 'False'}
        response1 = client.post('/api/maintenancemanagement/files/', data, format='multipart')
        pk = response1.data['id']
        response = client.get('/api/maintenancemanagement/files/' + str(pk) + '/')
        path = settings.BASE_DIR + response.data["file"]
        with Image.open(path) as img:
            colors = img.getcolors()
        self.assertEqual(colors, [(3600, 255)])

    def test_view_file_details_without_connected(self):
        """
            Test if a user without perm can't see a file detail
        """
        user = self.set_up_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_image('png'), 'is_manual': 'False'}
        response1 = client.post('/api/maintenancemanagement/files/', data, format='multipart')
        pk = response1.data['id']
        user.user_permissions.clear()
        client = APIClient()
        user = UserProfile.objects.get(id=user.pk)
        response = client.get('/api/maintenancemanagement/files/' + str(pk) + '/')
        self.assertEqual(response.status_code, 401)

    def test_delete_file_with_connected(self):
        """
            Test if a user with perm can delete a file
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_image('png'), 'is_manual': 'False'}
        response1 = client.post('/api/maintenancemanagement/files/', data, format='multipart')
        pk = response1.data['id']
        response = client.delete('/api/maintenancemanagement/files/' + str(pk) + '/')
        self.assertEqual(response.status_code, 204)

    def test_delete_file_without_connected(self):
        """
            Test if a user without perm can delete a file
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_image('png'), 'is_manual': 'False'}
        response1 = client.post('/api/maintenancemanagement/files/', data, format='multipart')
        pk = response1.data['id']
        user.user_permissions.clear()
        client = APIClient()
        user = UserProfile.objects.get(id=user.pk)
        response = client.delete('/api/maintenancemanagement/files/' + str(pk) + '/')
        self.assertEqual(response.status_code, 401)

    # Adding
    # this
    # line
    # because
    # of
    # SonarQube
