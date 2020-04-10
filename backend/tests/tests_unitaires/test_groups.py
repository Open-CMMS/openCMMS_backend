from django.test import TestCase, Client, RequestFactory
from usersmanagement.models import UserProfile, Team
from django.contrib.auth.models import Permission
from usersmanagement.views.views_team import belongs_to_team
from usersmanagement.serializers import UserProfileSerializer, TeamSerializer, PermissionSerializer, TacheSerializer

class TeamsTests(TestCase):

    def setUp(self):
        #Creation of the 2 inital teams
        Team.objects.create(name="Administrateur")
        Team.objects.create(name="Equipe de maintenance")

        #Creation of the 2 initial set of permissions
        PermissionSet.objects.create(name="admin_on_team",model_name="team",add=True,change=True,delete=True,view=True)
        PermissionSet.objects.create(name="equipe_maintenance_on_team",model_name="team")

        #Apply the 2 initial set of permissions on the 2 initial teams
        PermissionSet.objects.get(name="admin_on_team").apply("Administrateur")
        PermissionSet.objects.get(name="equipe_maintenance_on_team").apply("Equipe de maintenance")

        User_Profile.objects.create(first_name="Florent",
                                       last_name="B",
                                       email="florent.b@insa-rouen.fr",
                                       password="p@sword-au-top4",
                                        username = "FB1")

        User_Profile.objects.create(first_name="Hugo",
                                       last_name="SM",
                                       email="hugo.sm@insa-rouen.fr",
                                       password="p@sword-au-top4",
                                        username = "HSM")

        User_Profile.objects.create(first_name="Joran",
                                       last_name="Marie",
                                       email="joran.marie2@insa-rouen.fr",
                                       password="p@sword-au-top",
                                       username = "JoranMarie1")

        team = Team.objects.get(name="Equipe de maintenance")
        user = User_Profile.objects.get(username="FB1")
        team.user_set.add(user)

        team = Team.objects.get(name="Administrateur")
        user = User_Profile.objects.get(username="JoranMarie1")
        team.user_set.add(user)

        team = Team.objects.get(name="Administrateur")
        user = User_Profile.objects.get(username="HSM")
        team.user_set.add(user)



    def test_add_user_to_team_post_authorized(self):
        c = Client()

        joran = User_Profile.objects.get(username="JoranMarie1")
        c.force_login(joran)

        response = c.post("/gestion/add_user_to_team",{'username':'FB1','team_name':'Administrateur'})
        user = User_Profile.objects.get(username="FB1")
        team = Team.objects.get(name="Administrateur")

        self.assertEqual(response.status_code,201)
        self.assertEqual(user.teams.get(name="Administrateur"),team)


    def test_add_user_to_team_post_unauthorized(self):
        c = Client()

        florent = User_Profile.objects.get(username="FB1")
        c.force_login(florent)

        response = c.post("/gestion/add_user_to_team",{'username':'FB1','team_name':'Administrateur'})

        self.assertEqual(response.status_code,401)


    def test_add_user_to_team_put_authorized(self):
        c = Client()

        joran = User_Profile.objects.get(username="JoranMarie1")
        c.force_login(joran)

        response = c.put("/gestion/add_user_to_team",{'username':'HSM','team_name':'Administrateur'},content_type="application/json")
        user = User_Profile.objects.get(username="HSM")
        team = Team.objects.get(name="Administrateur")


        self.assertEqual(response.status_code,201)
        self.assertFalse(user.teams.filter(name="Administrateur").exists())

    def test_add_user_to_team_put_unauthorized(self):
        c = Client()

        florent = User_Profile.objects.get(username="FB1")
        c.force_login(florent)

        response = c.put("/gestion/add_user_to_team",{'username':'HSM','team_name':'Administrateur'},content_type="application/json")

        self.assertEqual(response.status_code,401)


    def test_team_list_get_authorized(self):

        teams = Team.objects.all()
        serializer = TeamSerializer(teams, many=True)

        c = Client()

        joran = User_Profile.objects.get(username="JoranMarie1")
        c.force_login(joran)

        response = c.get("/gestion/teams/")

        self.assertEqual(response.status_code,200)
        self.assertEqual(serializer.data, response.json())


    def test_team_list_get_unauthorized(self):

        c = Client()

        florent = User_Profile.objects.get(username="FB1")
        c.force_login(florent)

        response = c.get("/gestion/teams/")

        self.assertEqual(response.status_code,401)


    def test_team_list_post_authorized(self):

        c = Client()

        joran = User_Profile.objects.get(username="JoranMarie1")
        c.force_login(joran)

        response = c.post("/gestion/teams/",{"name":"test_team"})

        self.assertEqual(response.status_code,201)
        self.assertTrue(Team.objects.filter(name="test_team"))


    def test_team_list_post_unauthorized(self):

        c = Client()

        florent = User_Profile.objects.get(username="FB1")
        c.force_login(florent)

        response = c.post("/gestion/teams/",{"name":"test_team"})

        self.assertEqual(response.status_code,401)


    def test_team_detail_get_authorized(self):

        team = Team.objects.get(id="1")
        serializer = TeamSerializer(team)

        c = Client()

        joran = User_Profile.objects.get(username="JoranMarie1")
        c.force_login(joran)

        response = c.get("/gestion/teams/1")

        self.assertEqual(response.status_code,200)
        self.assertEqual(serializer.data, response.json())


    def test_team_detail_get_unauthorized(self):

        c = Client()

        florent = User_Profile.objects.get(username="FB1")
        c.force_login(florent)

        response = c.get("/gestion/teams/1")

        self.assertEqual(response.status_code,401)


    def test_team_detail_put_authorized(self):

        c = Client()

        joran = User_Profile.objects.get(username="JoranMarie1")
        c.force_login(joran)

        response = c.put("/gestion/teams/1", {"name":"new_name"}, content_type="application/json")

        team = Team.objects.get(id="1")

        self.assertEqual(response.status_code,200)
        self.assertEqual(team.name,"new_name")


    def test_team_detail_put_unauthorized(self):

        c = Client()

        florent = User_Profile.objects.get(username="FB1")
        c.force_login(florent)

        response = c.put("/gestion/teams/1", {"name":"new_name"}, content_type="application/json")

        self.assertEqual(response.status_code,401)


    def test_team_detail_delete_authorized(self):

        c = Client()

        joran = User_Profile.objects.get(username="JoranMarie1")
        c.force_login(joran)

        response = c.delete("/gestion/teams/1")

        self.assertEqual(response.status_code,204)
        self.assertFalse(Team.objects.filter(id="1").exists())


    def test_team_detail_delete_unauthorized(self):

        c = Client()

        florent = User_Profile.objects.get(username="FB1")
        c.force_login(florent)

        response = c.delete("/gestion/teams/1")

        self.assertEqual(response.status_code,401)


    def test_belongs_to_team_true(self):

        florent = User_Profile.objects.get(username="FB1")

        team = Team.objects.get(name="Equipe de maintenance")

        self.assertTrue(belongs_to_team(florent,team))


    def test_belongs_to_team_false(self):

        florent = User_Profile.objects.get(username="FB1")

        team = Team.objects.get(name="Administrateur")

        self.assertFalse(belongs_to_team(florent,team))
