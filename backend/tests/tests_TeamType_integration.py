from django.test import TestCase
from django.contrib.auth.models import Permission
from usersmanagement.models import TeamType,UserProfile,Team
from usersmanagement.serializers import TeamTypeSerializer
from rest_framework.test import APIClient

class TeamTypeTests(TestCase):

    def setUp(self):
        admin_type = TeamType.objects.create(name="Administrators")
        admin_team = Team.objects.create(name="Administrators")
        admin_team.set_team_type(admin_type)

    def add_view_perm(self,user):
        perm_view = Permission.objects.get(codename="view_teamtype")
        user.user_permissions.set([perm_view])

    def add_add_perm(self,user):
        perm_add = Permission.objects.get(codename="add_teamtype")
        user.user_permissions.set([perm_add])

    def add_change_perm(self,user):
        perm_change = Permission.objects.get(codename="change_teamtype")
        user.user_permissions.set([perm_change])

    def add_delete_perm(self,user):
        perm_delete = Permission.objects.get(codename="delete_teamtype")
        user.user_permissions.set([perm_delete])

    def test_teamtypes_list_get_authorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        teamtypes = TeamType.objects.all()
        serializer = TeamTypeSerializer(teamtypes, many=True)
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/usersmanagement/teamtypes/")
        self.assertEqual(response.status_code,200)
        self.assertEqual(serializer.data, response.json())

    def test_teamtypes_list_get_unauthorized(self):
        user = UserProfile.objects.create(username="user")
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.get("/api/usersmanagement/teamtypes/")
        self.assertEqual(response.status_code,401)

    def test_teamtypes_list_post_authorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)

        response = c.post("/api/usersmanagement/teamtypes/",{"name": "test_teamtype",
                                                    "perms":[3],
                                                    "team_set":[Team.objects.get(name="Administrators").id]}, format='json')
        self.assertEqual(response.status_code,201)
        self.assertTrue(TeamType.objects.get(name="test_teamtype"))


    def test_teamtypes_list_post_unauthorized(self):
        user = UserProfile.objects.create(username="user")
        c = APIClient()
        c.force_authenticate(user=user)
        response = c.post("/api/usersmanagement/teamtypes/",{"name": "test_teamtype",
                                                    "perms":[3],
                                                    "team_set":[Team.objects.get(name="Administrators").id]}, format='json')
        self.assertEqual(response.status_code,401)

    def test_teamtypes_detail_get_authorized(self):
        user = UserProfile.objects.create(username="user")
        self.add_view_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)

        team_type = TeamType.objects.get(name="Administrators")
        serializer = TeamTypeSerializer(team_type)
        response = c.get("/api/usersmanagement/teamtypes/"+str(team_type.id)+"/")
        self.assertEqual(response.status_code,200)
        self.assertEqual(serializer.data, response.json())

    def test_teamtypes_detail_get_unauthorized(self):
        user = UserProfile.objects.create(username="user")
        c = APIClient()
        c.force_authenticate(user=user)
        team_type = TeamType.objects.get(name="Administrators")
        response = c.get("/api/usersmanagement/teamtypes/" + str(team_type.id) + "/")
        self.assertEqual(response.status_code,401)

    def test_teamtypes_detail_put_authorized(self):
        user = UserProfile.objects.create(username="user")
        self.add_change_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        team_type = TeamType.objects.get(name="Administrators")

        response = c.put("/api/usersmanagement/teamtypes/" + str(team_type.id) + "/",{
                                                    "name": "test_teamtype",
                                                    "perms":[3],
                                                    "team_set":[Team.objects.get(name="Administrators").id]}, format='json')

        self.assertEqual(response.status_code,200)
        self.assertTrue(TeamType.objects.get(name="test_teamtype"))

    def test_teamtypes_detail_put_unauthorized(self):
        user = UserProfile.objects.create(username="user")
        c = APIClient()
        c.force_authenticate(user=user)
        team_type = TeamType.objects.get(name="Administrators")

        response = c.put("/api/usersmanagement/teamtypes/" + str(team_type.id) + "/", {
            "name": "test_teamtype",
            "perms": [3],
            "team_set": [Team.objects.get(name="Administrators").id]}, format='json')

        self.assertEqual(response.status_code, 401)

    def test_teamtypes_delete_authorized(self):
        user = UserProfile.objects.create(username="user")
        self.add_delete_perm(user)
        c = APIClient()
        c.force_authenticate(user=user)
        team_type = TeamType.objects.get(name="Administrators")
        response = c.delete("/api/usersmanagement/teamtypes/" + str(team_type.id) + "/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(TeamType.objects.filter(id=team_type.id).exists())

    def test_teamtypes_delete_authorized(self):
        user = UserProfile.objects.create(username="user")
        c = APIClient()
        c.force_authenticate(user=user)
        team_type = TeamType.objects.get(name="Administrators")
        response = c.delete("/api/usersmanagement/teamtypes/"+str(team_type.id)+"/")
        self.assertEqual(response.status_code,401)
