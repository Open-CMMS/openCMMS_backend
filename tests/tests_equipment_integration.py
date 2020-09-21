from django.contrib.auth.models import Permission
from django.test import TestCase
from maintenancemanagement.models import Equipment, EquipmentType, File
from maintenancemanagement.serializers import EquipmentSerializer
from openCMMS import settings
from rest_framework.test import APIClient
from usersmanagement.models import UserProfile

User = settings.AUTH_USER_MODEL


class EquipmentTests(TestCase):
    def setUp(self):
        """
        Set up an equipment with a name, an equipment type
        """
        v = EquipmentType.objects.create(name="Voiture")
        Equipment.objects.create(name="Peugeot Partner", equipment_type=v)

    def temporary_file(self):
        """
        Returns a new temporary file
        """
        import tempfile

        tmp_file = tempfile.TemporaryFile()
        tmp_file.write(b"Coco veut un gateau")
        tmp_file.seek(0)
        return tmp_file

    def add_add_perm_file(self, user):
        """
        Add add permission for file
        """
        permission = Permission.objects.get(codename="add_file")
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

    def test_equipment_list_get_authorized(self):
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

    def test_equipment_list_get_unauthorized(self):
        """
        Test if a user without perm doesn't receive the equipments' list
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        equipments = Equipment.objects.all()
        serializer = EquipmentSerializer(equipments, many=True)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/maintenancemanagement/equipments/")
        self.assertEqual(response.status_code, 401)

    def test_equipment_list_post_authorized(self):
        """
        Test if a user with perm can add an equipment
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.post(
            "/api/maintenancemanagement/equipments/",
            {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Equipment.objects.get(name="Renault Kangoo"))

    def test_equipment_list_post_unauthorized(self):
        """
        Test if a user without perm can't add an equipment
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.post(
            "/api/maintenancemanagement/equipments/",
            {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
            },
        )
        self.assertEqual(response.status_code, 401)

    def test_equipment_detail_get_authorized(self):
        """
        Test if a user with perm can receive the equipment data
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)

        equipment = Equipment.objects.get(name="Peugeot Partner")
        serializer = EquipmentSerializer(equipment)
        response = c.get(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_equipment_detail_get_unauthorized(self):
        """
        Test if a user without perm can't receive the equipment data
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)

        equipment = Equipment.objects.get(name="Peugeot Partner")
        serializer = EquipmentSerializer(equipment)
        response = c.get(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/"
        )
        self.assertEqual(response.status_code, 401)

    def test_equipment_detail_put_authorized(self):
        """
        Test if a user with perm can change an equipment
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_change_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Peugeot Partner")
        response = c.put(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/",
            {"name": "Renault Trafic"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Equipment.objects.get(name="Renault Trafic"))

    def test_equipment_detail_put_unauthorized(self):
        """
        Test if a user without perm can't change an equipment
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Peugeot Partner")
        response = c.put(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/",
            {"name": "Renault Trafic"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_equipment_detail_delete_authorized(self):
        """
        Test if a user with perm can delete an equipment
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_delete_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Peugeot Partner")
        response = c.delete(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/"
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Equipment.objects.filter(id=equipment.id).exists())

    def test_equipment_detail_delete_unauthorized(self):
        """
        Test if a user without perm can't delete an equipment
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Peugeot Partner")
        response = c.delete(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/"
        )
        self.assertEqual(response.status_code, 401)

    def test_equipment_list_post_authorized_with_file(self):
        """
        Test if a user with perm can add an equipment with a file
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm_file(user)
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {"file": self.temporary_file(), "is_manual": "False"}
        response1 = c.post(
            "/api/maintenancemanagement/files/", data, format="multipart"
        )
        pk = response1.data["id"]
        response = c.post(
            "/api/maintenancemanagement/equipments/",
            {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_equipment_list_post_unauthorized_with_file(self):
        """
        Test if a user without perm can't add an equipment with a file
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm_file(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {"file": self.temporary_file(), "is_manual": "False"}
        response1 = c.post(
            "/api/maintenancemanagement/files/", data, format="multipart"
        )
        pk = response1.data["id"]
        response = c.post(
            "/api/maintenancemanagement/equipments/",
            {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_equipment_detail_get_authorized_with_file(self):
        """
        Test if a user with perm can receive the equipment data with a file
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        self.add_add_perm(user)
        self.add_add_perm_file(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {"file": self.temporary_file(), "is_manual": "False"}
        response1 = c.post(
            "/api/maintenancemanagement/files/", data, format="multipart"
        )
        pk = response1.data["id"]
        response = c.post(
            "/api/maintenancemanagement/equipments/",
            {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk],
            },
            format="json",
        )
        equipment = Equipment.objects.get(name="Renault Kangoo")
        serializer = EquipmentSerializer(equipment)
        response = c.get(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_equipment_detail_get_unauthorized_with_file(self):
        """
        Test if a user without perm can't receive the equipment data with a file
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        self.add_add_perm_file(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {"file": self.temporary_file(), "is_manual": "False"}
        response1 = c.post(
            "/api/maintenancemanagement/files/", data, format="multipart"
        )
        pk = response1.data["id"]
        response = c.post(
            "/api/maintenancemanagement/equipments/",
            {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk],
            },
            format="json",
        )
        equipment = Equipment.objects.get(name="Renault Kangoo")
        serializer = EquipmentSerializer(equipment)
        response = c.get(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/"
        )
        self.assertEqual(response.status_code, 401)

    def test_equipment_list_post_authorized_with_files(self):
        """
        Test if a user with perm can add an equipment with multiple files
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm_file(user)
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {"file": self.temporary_file(), "is_manual": "False"}
        data2 = {"file": self.temporary_file(), "is_manual": "True"}
        response1 = c.post(
            "/api/maintenancemanagement/files/", data, format="multipart"
        )
        response2 = c.post(
            "/api/maintenancemanagement/files/", data2, format="multipart"
        )
        pk_1 = response1.data["id"]
        pk_2 = response2.data["id"]
        response = c.post(
            "/api/maintenancemanagement/equipments/",
            {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk_1, pk_2],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_equipment_list_post_unauthorized_with_files(self):
        """
        Test if a user without perm can't add an equipment with multiple files
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm_file(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {"file": self.temporary_file(), "is_manual": "False"}
        data2 = {"file": self.temporary_file(), "is_manual": "True"}
        response1 = c.post(
            "/api/maintenancemanagement/files/", data, format="multipart"
        )
        response2 = c.post(
            "/api/maintenancemanagement/files/", data2, format="multipart"
        )
        pk_1 = response1.data["id"]
        pk_2 = response2.data["id"]
        response = c.post(
            "/api/maintenancemanagement/equipments/",
            {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk_1, pk_2],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_equipment_detail_get_authorized_with_files(self):
        """
        Test if a user with perm can receive the equipment data with multiple files
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        self.add_add_perm(user)
        self.add_add_perm_file(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {"file": self.temporary_file(), "is_manual": "False"}
        data2 = {"file": self.temporary_file(), "is_manual": "True"}
        response1 = c.post(
            "/api/maintenancemanagement/files/", data, format="multipart"
        )
        response2 = c.post(
            "/api/maintenancemanagement/files/", data2, format="multipart"
        )
        pk_1 = response1.data["id"]
        pk_2 = response2.data["id"]
        response = c.post(
            "/api/maintenancemanagement/equipments/",
            {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk_1, pk_2],
            },
            format="json",
        )
        equipment = Equipment.objects.get(name="Renault Kangoo")
        serializer = EquipmentSerializer(equipment)
        response = c.get(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.data, response.json())

    def test_equipment_detail_get_unauthorized_with_files(self):
        """
        Test if a user without perm can't receive the equipment data with multiple files
        """
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        self.add_add_perm_file(user)
        c = APIClient()
        c.force_authenticate(user=user)
        data = {"file": self.temporary_file(), "is_manual": "False"}
        data2 = {"file": self.temporary_file(), "is_manual": "True"}
        response1 = c.post(
            "/api/maintenancemanagement/files/", data, format="multipart"
        )
        pk_1 = response1.data["id"]
        response2 = c.post(
            "/api/maintenancemanagement/files/", data2, format="multipart"
        )
        pk_2 = response2.data["id"]
        response = c.post(
            "/api/maintenancemanagement/equipments/",
            {
                "name": "Renault Kangoo",
                "equipment_type": EquipmentType.objects.get(name="Voiture").id,
                "files": [pk_1, pk_2],
            },
            format="json",
        )
        equipment = Equipment.objects.get(name="Renault Kangoo")
        serializer = EquipmentSerializer(equipment)
        response = c.get(
            "/api/maintenancemanagement/equipments/" + str(equipment.id) + "/"
        )
        self.assertEqual(response.status_code, 401)
