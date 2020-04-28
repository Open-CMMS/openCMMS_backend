from django.test import TestCase
from .models import Equipment
from rest_framework.test import APIClient


class EquipmentTests(TestCase):

    def setUp(self):
        EquipmentType.objects.create(name="Voiture")

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
        self.add_view_perm(user)
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
            "name"= "Renault Kangoo",
            "equipment_type"= [EquipmentType.objects.get(name="Voiture").id]
        })
        self.assertEqual(response.status_code,201)
        self.assertTrue(Equipment.objects.get(name="Renault Kangoo"))

    def test_equipment_list_post_unauthorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.post("/api/maintenancemanagement/equipment/", {
            "name" = "Renault Kangoo",
                     "equipment_type" = [EquipmentType.objects.get(name="Voiture").id]
        })
        self.assertEqual(response.status_code, 401)

