from django.test import TestCase
from django.contrib.auth.models import Permission
from maintenancemanagement.models import Equipment, EquipmentType
from usersmanagement.models import UserProfile
from rest_framework.test import APIClient
from maintenancemanagement.serializers import EquipmentSerializer
from openCMMS import settings

User = settings.AUTH_USER_MODEL

class EquipmentTests(TestCase):

    def setUp(self):
        v= EquipmentType.objects.create(name="Voiture")
        Equipment.objects.create(name="Peugeot Partner", equipment_type=v)

    def add_view_perm(self, user):
            perm_view = Permission.objects.get(codename="view_equipment")
            user.user_permissions.set([perm_view])

    def add_add_perm(self, user):
            perm_add = Permission.objects.get(codename="add_equipment")
            user.user_permissions.set([perm_add])

    def add_change_perm(self, user):
            perm_change = Permission.objects.get(codename="change_equipment")
            user.user_permissions.set([perm_change])

    def add_delete_perm(self, user):
            perm_delete = Permission.objects.get(codename="delete_equipment")
            user.user_permissions.set([perm_delete])


    def test_equipment_list_get_authorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        equipments = Equipment.objects.all()
        serializer = EquipmentSerializer(equipments, many=True)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/maintenancemanagement/equipment/")
        self.assertEqual(response.status_code,200)
        self.assertEqual(serializer.data, response.json())

    def test_equipment_list_get_unauthorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        equipments = Equipment.objects.all()
        serializer = EquipmentSerializer(equipments, many=True)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/maintenancemanagement/equipment/")
        self.assertEqual(response.status_code, 401)

    def test_equipment_list_post_authorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.post("/api/maintenancemanagement/equipment/", {
            "name": "Renault Kangoo",
            "equipment_type": [EquipmentType.objects.get(name="Voiture").id]
        }, format='json')
        self.assertEqual(response.status_code,201)
        self.assertTrue(Equipment.objects.get(name="Renault Kangoo"))

    def test_equipment_list_post_unauthorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.post("/api/maintenancemanagement/equipment/", {
            "name" : "Renault Kangoo",
                     "equipment_type" : [EquipmentType.objects.get(name="Voiture").id]
        })
        self.assertEqual(response.status_code, 401)

    def test_equipment_detail_get_authorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)

        equipment = Equipment.objects.get(name="Peugeot Partner")
        serializer = EquipmentSerializer(equipment)
        response = c.get("/api/maintenancemanagement/equipment/"+str(equipment.id)+"/")
        self.assertEqual(response.status_code,200)
        self.assertEqual(serializer.data, response.json())

    def test_equipment_detail_get_unauthorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)

        equipment = Equipment.objects.get(name="Peugeot Partner")
        serializer = EquipmentSerializer(equipment)
        response = c.get("/api/maintenancemanagement/equipment/"+str(equipment.id)+"/")
        self.assertEqual(response.status_code,401)

    def test_equipment_detail_put_authorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Peugeot Partner")
        response = c.put("/api/maintenancemanagement/equipment/"+str(equipment.id)+"/",
                         {
                             "name":"Renault Trafic"
                         }, format='json')
        self.assertEqual(response.status_code,200)
        self.assertTrue(Equipment.objects.get(name="Renault Trafic"))

    def test_equipment_detail_put_unauthorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Peugeot Partner")
        response = c.put("/api/maintenancemanagement/equipment/"+str(equipment.id)+"/",
                         {
                             "name":"Renault Trafic"
                         }, format='json')
        self.assertEqual(response.status_code,401)

    def test_equipment_detail_delete_authorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_delete_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Peugeot Partner")
        response = c.delete("/api/maintenancemanagement/equipmenet/"+str(equipment.id)+"/")
        self.assertEqual(response.status_code,204)
        self.assertFalse(Equipment.objects.filter(id=equipment.id).exists())


    def test_equipment_detail_delete_authorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        c = APIClient()
        c.force_authenticate(user=user)
        equipment = Equipment.objects.get(name="Peugeot Partner")
        response = c.delete("/api/maintenancemanagement/equipmenet/"+str(equipment.id)+"/")
        self.assertEqual(response.status_code,401)


