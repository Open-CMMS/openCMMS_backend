from django.contrib.auth.models import Permission
from django.test import TestCase, Client
from usersmanagement.models import TeamType,Team,UserProfile
from usersmanagement.serializers import TeamTypeSerializer

class TeamTypeTests(TestCase):

    def setUp(self):
        perm_1 = Permission.objects.get(id=1)
        perm_2 = Permission.objects.get(id=2)
        admin_type = TeamType.objects.create(name="Administrators")
        admin_team = Team.objects.create(name="Administrators")
        admin_team.set_team_type(admin_type)
        admin_type.perms.add(perm_1, perm_2)

    def add_view_perm(self,user):
        perm_view = Permission.objects.get(codename="view_teamtype")
        user.user_permissions.set([perm_view])

    def add_add_perm(self,user):
        perm_add = Permission.objects.get(codename="add_teamtype")
        user.user_permissions.set([perm_add])

    def test_get_team_type(self):
        MaintenanceManager_type = TeamType.objects.create(name="Maintenance Manager")
        self.assertEqual(MaintenanceManager_type, TeamType.objects.get(name="Maintenance Manager"))

    def test_set_perm(self):
        perm = Permission.objects.get(id=1)
        MaintenanceManager_type = TeamType.objects.create(name="Maintenance Manager")
        MaintenanceManager_type.perms.add(perm)
        self.assertEqual(MaintenanceManager_type.perms.get(id=1),perm)

    def test_apply_(self):
        admin_type = TeamType.objects.get(name="Administrators")
        admin_type._apply_()
        admin_team = Team.objects.get(name="Administrators")
        self.assertEqual(admin_team.permissions.get(id=1),Permission.objects.get(id=1))
        self.assertEqual(admin_team.permissions.get(id=2), Permission.objects.get(id=2))

    def test_apply_new_teamtype(self):
        perm_3 = Permission.objects.get(id=3)
        MaintenanceManager_type = TeamType.objects.create(name="Maintenance Manager")
        MaintenanceManager_type.perms.add(perm_3)
        admin_team = Team.objects.get(name="Administrators")
        admin_team.set_team_type(MaintenanceManager_type)
        self.assertEqual(admin_team.permissions.get(id=3), perm_3)

    def test_teamtypes_list_get_authorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_view_perm(user)
        teamtypes = TeamType.objects.all()
        serializer = TeamTypeSerializer(teamtypes, many=True)
        c = Client()
        c.force_login(user)
        response = c.get("/api/gestion/teamtypes/")
        self.assertEqual(response.status_code,200)
        self.assertEqual(serializer.data, response.json())

    def test_teamtypes_list_get_unauthorized(self):
        user = UserProfile.objects.create(username="user")
        c = Client()
        c.force_login(user)
        response = c.get("/api/gestion/teamtypes/")
        self.assertEqual(response.status_code,401)

    def test_teamtypes_list_post_authorized(self):
        user = UserProfile.objects.create(username="user", password="p4ssword")
        self.add_add_perm(user)
        c = Client()
        c.force_login(user)

        response = c.post("/api/gestion/teamtypes/",{
                                                    "id": 7,
                                                    "name": "test_teamtype",
                                                    "perms":[3],
                                                    "team_set":[1]})
        self.assertEqual(response.status_code,200)
        self.assertTrue(TeamType.objects.filter(name="test_teamtype"))

    def test_teamtypes_list_post_unauthorized(self):
        user = UserProfile.objects.create(username="user")
        c = Client()
        c.force_login(user)
        response = c.get("/api/gestion/teamtypes/")
        self.assertEqual(response.status_code,401)

    def test_teamtypes_detail_get_authorized(self):
        user = UserProfile.objects.create(username="user")
        self.add_view_perm(user)
        c = Client()
        c.force_login(user)

        team_type = TeamType.objects.get(id=1)
        serializer = TeamTypeSerializer(team_type)

        response = c.get("/api/gestion/teamtypes/1")
        self.assertEqual(response.status_code,200)
        self.assertEqual(serializer.data, response.json())


