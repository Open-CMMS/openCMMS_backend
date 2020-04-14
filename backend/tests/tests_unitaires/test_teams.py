from django.test import TestCase, RequestFactory
from rest_framework.test import APIClient
from usersmanagement.models import UserProfile, Team, TeamType
from django.contrib.auth.models import Permission
from usersmanagement.views.views_team import belongs_to_team
from usersmanagement.serializers import UserProfileSerializer, TeamSerializer, PermissionSerializer
from django.contrib.contenttypes.models import ContentType

class TeamsTests(TestCase):

    def set_up(self):
        #Creation of 3 TeamTypes
        Admins = TeamType.objects.create(name="Administrators")
        MMs = TeamType.objects.create(name="Maintenance Manager")
        MTs = TeamType.objects.create(name="Maintenance Team")

        #Create and add permissions du admin
        content_type = ContentType.objects.get_for_model(Team)
        permission = Permission.objects.create(codename='add_Team',
                                       name='Can add a team',
                                       content_type=content_type)
        permission2 = Permission.objects.create(codename='view_Team',
                                       name='Can view a team',
                                       content_type=content_type)
        permission3 = Permission.objects.create(codename='delete_Team',
                                       name='Can delete a team',
                                       content_type=content_type)
        permission4 = Permission.objects.create(codename='change_Team',
                                       name='Can change a team',
                                       content_type=content_type)

        #Creation of the 3 inital Teams
        T_Admin = Team.objects.create(name="Administrators 1", team_type=Admins)
        T_MM1 = Team.objects.create(name="Maintenance Manager 1", team_type=MMs)
        T_MT1 = Team.objects.create(name="Maintenance Team 1", team_type=MTs)

        #User creation
        tom = UserProfile.objects.create(first_name="Tom",
                                       last_name="N",
                                       email="tom.n@ac.com",
                                       password="truc",
                                       username = "tn")

        joe = UserProfile.objects.create(first_name="Joe",
                                       last_name="D",
                                       email="joe.d@ll.com",
                                       password="bouh",
                                       username = "jd")

        joey = UserProfile.objects.create(first_name="Joey",
                                       last_name="Bidouille",
                                       email="joey.bidouille@machin.com",
                                       password="brico",
                                       username = "jbi")

        tom.groups.add(T_Admin)
        tom.save()
        tom.user_permissions.add(permission)
        tom.user_permissions.add(permission2)
        tom.user_permissions.add(permission3)
        tom.user_permissions.add(permission4)
        tom.save()

        joe.groups.add(T_MT1)
        joe.save()

    def test_add_user_to_team_post_authorized(self):
        self.set_up()
        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_login(tom)

        response = c.post("/api/usersmanagement/add_user_to_team",{'username':'jd','team_name':'Administrators 1'}, format='json')
        user = UserProfile.objects.get(username="jd")
        team = Team.objects.get(name="Administrators 1")

        self.assertEqual(response.status_code,201)
        self.assertEqual(user.groups.get(name="Administrators 1").name,team.name)

    def test_add_user_to_team_post_unauthorized(self):
        self.set_up()
        c = APIClient()

        joey = UserProfile.objects.get(username="jbi")
        c.force_login(joey)

        response = c.post("/api/usersmanagement/add_user_to_team",{'username':'jbi','team_name':'Administrators 1'})

        self.assertEqual(response.status_code,401)


    def test_add_user_to_team_put_authorized(self):
        self.set_up()
        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_login(tom)

        response = c.put("/api/usersmanagement/add_user_to_team",{'username':'jd','team_name':'Administrators 1'}, format='json')
        user = UserProfile.objects.get(username="jd")
        team = Team.objects.get(name="Administrators 1")

        self.assertEqual(response.status_code,201)
        self.assertFalse(user.groups.filter(name="Administrators 1").exists())

    def test_add_user_to_team_put_unauthorized(self):
        self.set_up()
        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_login(joe)

        response = c.put("/api/usersmanagement/add_user_to_team",{'username':'jbi','team_name':'Administrators 1'}, format='json')

        self.assertEqual(response.status_code,401)


    def test_team_list_get_authorized(self):
        self.set_up()

        teams = Team.objects.all()
        serializer = TeamSerializer(teams, many=True)

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_login(tom)

        response = c.get("/api/usersmanagement/teams/")

        self.assertEqual(response.status_code,200)
        self.assertEqual(serializer.data, response.json())


    def test_team_list_get_unauthorized(self):
        self.set_up()

        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_login(joe)

        response = c.get("/api/usersmanagement/teams/")

        self.assertEqual(response.status_code,401)


    def test_team_list_post_authorized(self):
        self.set_up()

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_login(tom)

        tt = TeamType.objects.all()[0]

        response = c.post("/api/usersmanagement/teams/",{"name":"test_team", "team_type":str(tt.id)})
        team = Team.objects.get(pk=response.data['id'])
        self.assertEqual(response.status_code,201)
        self.assertTrue(Team.objects.filter(name="test_team"))
        self.assertEqual(team.team_type, tt)


    def test_team_list_post_unauthorized(self):
        self.set_up()

        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_login(joe)

        response = c.post("/api/usersmanagement/teams/",{"name":"test_team"})

        self.assertEqual(response.status_code,401)


    def test_team_detail_get_authorized(self):
        self.set_up()

        team = Team.objects.get(name="Administrators 1")
        serializer = TeamSerializer(team)

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_login(tom)

        address = "/api/usersmanagement/teams/"+str(team.id)

        response = c.get(address)

        self.assertEqual(response.status_code,200)
        self.assertEqual(serializer.data, response.json())


    def test_team_detail_get_unauthorized(self):
        self.set_up()

        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_login(joe)

        team = Team.objects.get(name="Administrators 1")

        address = "/api/usersmanagement/teams/"+str(team.id)

        response = c.get(address)

        self.assertEqual(response.status_code,401)


    def test_team_detail_put_change_name_authorized(self):
        self.set_up()

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_login(tom)

        team = Team.objects.get(name="Administrators 1")
        address = "/api/usersmanagement/teams/"+str(team.id)

        response = c.put(address,{"name":"new_name"}, format='json')
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['name'],"new_name")

    def test_team_detail_put_change_team_type_authorized(self):
        self.set_up()

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_login(tom)

        team = Team.objects.get(name="Administrators 1")
        address = "/api/usersmanagement/teams/"+str(team.id)

        tt = TeamType.objects.all()[1]

        response = c.put(address,{"team_type":str(tt.id)}, format='json')
        
        teamApres = Team.objects.get(pk=response.data['id'])
        self.assertEqual(response.status_code,200)
        self.assertNotEqual(team.team_type, teamApres.team_type)


    def test_team_detail_put_unauthorized(self):
        self.set_up()

        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_login(joe)

        team = Team.objects.get(name="Administrators 1")

        address = "/api/usersmanagement/teams/"+str(team.id)

        response = c.put(address, {"name":"new_name"}, content_type="application/json")

        self.assertEqual(response.status_code,401)


    def test_team_detail_delete_authorized(self):
        self.set_up()

        c = APIClient()
        team = Team.objects.get(name="Maintenance Team 1")

        tom = UserProfile.objects.get(username="tn")
        c.force_login(tom)

        address = "/api/usersmanagement/teams/"+str(team.id)

        response = c.delete(address)

        self.assertEqual(response.status_code,204)
        with self.assertRaises(Team.DoesNotExist):
            team_final = Team.objects.get(name="Maintenance Team 1")


    def test_team_detail_delete_unauthorized(self):
        self.set_up()

        c = APIClient()
        team = Team.objects.get(name="Maintenance Team 1")

        joe = UserProfile.objects.get(username="jd")
        c.force_login(joe)

        address = "/api/usersmanagement/teams/"+str(team.id)

        response = c.delete(address)

        self.assertEqual(response.status_code,401)


    def test_belongs_to_team_true(self):
        self.set_up()

        joe = UserProfile.objects.get(username="jd")

        team = Team.objects.get(name="Maintenance Team 1")

        self.assertTrue(belongs_to_team(joe,team))


    def test_belongs_to_team_false(self):
        self.set_up()

        joe = UserProfile.objects.get(username="jd")

        team = Team.objects.get(name="Administrators 1")

        self.assertFalse(belongs_to_team(joe,team))