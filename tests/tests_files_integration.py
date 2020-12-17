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
        image = Image.new('1', (60, 60), 255)
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

    def test_files_TI2_can_acces_files_list_with_connected(self):
        """
        Test if a user with perm receive the data.

                Inputs:
                    user (UserProfile): a UserProfile we setup with no permissions on files.
                    serializer (FileSerializer): a FileSerializer containing all files of the database in a Serialized state.

                Expected Outputs:
                    We expect the response's data to be the same dict than the serialiser's data.
        """
        user = self.set_up_without_perm()
        file = File.objects.all()
        serializer = FileSerializer(file, many=True)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/maintenancemanagement/files/', format='json')
        self.assertEqual(response.data, serializer.data)

    def test_files_TI2_can_acces_file_list_without_connected(self):
        """
        Test if a client with no authenticated user can't access the file list.

                Inputs:
                    client (APIClient): the client that will be used to do the GET with no user authenticated.

                Expected Outputs:
                    We expect the response's status_code to be 401.
        """
        client = APIClient()
        response = client.get('/api/maintenancemanagement/files/', format='json')
        self.assertEqual(response.status_code, 401)

    def test_files_TI1_add_png_file_with_connected(self):
        """
        Test if a user can add a png file.

                Inputs:
                    user (UserProfile): a user we created with no permission.
                    file (BytesIO) : a File-like object containing a png picture we send with a POST.

                Expected Outputs:
                    We expect the response's status code to be 201.
        """
        user = self.set_up_without_perm()
        file = self.temporary_image('png')
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': file, 'is_manual': 'False'}
        response = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_files_TI1_add_jpg_file_with_connected(self):
        """
        Test if a user with perm can add a jpg file.

                Inputs:
                    user (UserProfile): a user we created with no permission.
                    file (BytesIO) : a File-like object containing a jpeg picture we send with a POST.

                Expected Outputs:
                    We expect the response's status code to be 201.
        """
        user = self.set_up_without_perm()
        file = self.temporary_image('JPEG')
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': file, 'is_manual': 'False'}
        response = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_files_TI1_add_bitmap_file_with_connected(self):
        """
        Test if a user with perm can add a file.

                Inputs:
                    user (UserProfile): a user we created with no permission.
                    file (BytesIO) : a File-like object containing a bitmap picture we send with a POST.

                Expected Outputs:
                    We expect the response's status code to be 201.
        """
        user = self.set_up_without_perm()
        file = self.temporary_image('BMP')
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': file, 'is_manual': 'False'}
        response = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_files_TI1_add_pdf_file_with_connected(self):
        """
        Test if a user with perm can add a pdf file.

                Inputs:
                    user (UserProfile): a user we created with no permission.
                    file (BytesIO) : a File-like object containing a pdf picture we send with a POST.

                Expected Outputs:
                    We expect the response's status code to be 201.
        """
        user = self.set_up_without_perm()
        file = self.temporary_image('PDF')
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': file, 'is_manual': 'False'}
        response = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        print(response.data)
        self.assertEqual(response.status_code, 201)

    def test_files_TI1_add_text_file_with_connected(self):
        """
        Test if a user can't add text file.

                Inputs:
                    user (UserProfile): a user we created with no permission.
                    file (BytesIO) : a File-like object containing a text file we send with a POST.

                Expected Outputs:
                    We expect the response's status code to be 400.
        """
        user = self.set_up_without_perm()
        file = self.temporary_file()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': file, 'is_manual': 'False'}
        response = client.post("/api/maintenancemanagement/files/", data, format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_add_file_without_connected(self):
        """
        Test if a client with no authenticated user can't add a file.

                Inputs:
                    client (APIClient): the client that will be used to do the POST with no user authenticated.

                Expected Outputs:
                    We expect the response's status_code to be 401.
        """
        client = APIClient()
        response = client.post('/api/maintenancemanagement/files/', format='multipart')
        self.assertEqual(response.status_code, 401)

    def test_files_TI3_view_file_details_with_connected(self):
        """
        Test if a user can see a file.

                Inputs:
                    user (UserProfile): a user we created with no permission.
                    file (BytesIO): a File-like object we use to create a file in the database so we cant check the GET method on a particular file.

                Expected Output:
                    We expect the image we receive to be the color of the one we created.

        """
        user = self.set_up_without_perm()
        file = self.temporary_image('png')
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': file, 'is_manual': 'False'}
        response1 = client.post('/api/maintenancemanagement/files/', data, format='multipart')
        pk = response1.data['id']
        response = client.get(f'/api/maintenancemanagement/files/{pk}/')
        path = settings.BASE_DIR + response.data["file"]
        with Image.open(path) as img:
            colors = img.getcolors()
        self.assertEqual(colors, [(3600, 255)])

    def test_files_TI3_view_file_details_without_connected(self):
        """
        Test if a client with no authenticated user can't access a file.

                Inputs:
                    client (APIClient): the client that will be used to do the GET with no user authenticated.

                Expected Outputs:
                    We expect the response's status_code to be 401.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_image('png'), 'is_manual': 'False'}
        response1 = client.post('/api/maintenancemanagement/files/', data, format='multipart')
        pk = response1.data['id']
        user.user_permissions.clear()
        client = APIClient()
        response = client.get(f'/api/maintenancemanagement/files/{pk}/')
        self.assertEqual(response.status_code, 401)

    def test_files_TI4_delete_file_with_connected(self):
        """
        Test if a user can delete a file.

                Inputs:
                    user (UserProfile): a user we created with no permission.
                    file (BytesIO): a File-like object we use to create a file in the database so we cant check the DELETE method on a particular file.

                Expected Output:
                    We expect the image we receive to be the color of the one we created.
        """
        user = self.set_up_without_perm()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': self.temporary_image('png'), 'is_manual': 'False'}
        response1 = client.post('/api/maintenancemanagement/files/', data, format='multipart')
        pk = response1.data['id']
        response = client.delete('/api/maintenancemanagement/files/' + str(pk) + '/')
        self.assertEqual(response.status_code, 204)

    def test_files_TI4_delete_file_without_connected(self):
        """
        Test if a client with no authenticated user can't delete a file.

                Inputs:
                    client (APIClient): the client that will be used to do the GET with no user authenticated.

                Expected Outputs:
                    We expect the response's status_code to be 401.
        """
        user = self.set_up_without_perm()
        file = self.temporary_image('png')
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'file': file, 'is_manual': 'False'}
        response1 = client.post('/api/maintenancemanagement/files/', data, format='multipart')
        pk = response1.data['id']
        user.user_permissions.clear()
        client = APIClient()
        user = UserProfile.objects.get(id=user.pk)
        response = client.delete(f'/api/maintenancemanagement/files/{pk}/')
        self.assertEqual(response.status_code, 401)
