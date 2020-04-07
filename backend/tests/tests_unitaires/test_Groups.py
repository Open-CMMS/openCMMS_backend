from django.urls import reverse
from django.test import TestCase, Client, RequestFactory
from django.core.exceptions import ValidationError
from gestion.models import PermissionSet,User_Profile
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import authenticate,login,logout
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from gestion.views import belongs_to_group
from gestion.serializers import User_ProfileSerializer, GroupSerializer, PermissionSerializer, PermissionSetSerializer, TacheSerializer

class GroupsTests(TestCase):

    def setUp(self):
        #Creation of the 2 inital groups
        Group.objects.create(name="Administrateur")
        Group.objects.create(name="Equipe de maintenance")

        #Creation of the 2 initial set of permissions
        PermissionSet.objects.create(name="admin_on_group",model_name="group",add=True,change=True,delete=True,view=True)
        PermissionSet.objects.create(name="equipe_maintenance_on_group",model_name="group")

        #Apply the 2 initial set of permissions on the 2 initial groups
        PermissionSet.objects.get(name="admin_on_group").apply("Administrateur")
        PermissionSet.objects.get(name="equipe_maintenance_on_group").apply("Equipe de maintenance")

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

        group = Group.objects.get(name="Equipe de maintenance")
        user = User_Profile.objects.get(username="FB1")
        group.user_set.add(user)

        group = Group.objects.get(name="Administrateur")
        user = User_Profile.objects.get(username="JoranMarie1")
        group.user_set.add(user)

        group = Group.objects.get(name="Administrateur")
        user = User_Profile.objects.get(username="HSM")
        group.user_set.add(user)
        


    def test_add_user_to_group_post_authorized(self):
        c = Client()

        joran = User_Profile.objects.get(username="JoranMarie1")
        c.force_login(joran)

        response = c.post("/gestion/add_user_to_group",{'username':'FB1','group_name':'Administrateur'})
        user = User_Profile.objects.get(username="FB1")
        group = Group.objects.get(name="Administrateur")

        self.assertEqual(response.status_code,201)
        self.assertEqual(user.groups.get(name="Administrateur"),group)


    def test_add_user_to_group_post_unauthorized(self):
        c = Client()

        florent = User_Profile.objects.get(username="FB1")
        c.force_login(florent)

        response = c.post("/gestion/add_user_to_group",{'username':'FB1','group_name':'Administrateur'})

        self.assertEqual(response.status_code,401)

    
    def test_add_user_to_group_put_authorized(self):
        c = Client()

        joran = User_Profile.objects.get(username="JoranMarie1")
        c.force_login(joran)

        response = c.put("/gestion/add_user_to_group",{'username':'HSM','group_name':'Administrateur'},content_type="application/json")
        user = User_Profile.objects.get(username="HSM")
        group = Group.objects.get(name="Administrateur")


        self.assertEqual(response.status_code,201)
        self.assertFalse(user.groups.filter(name="Administrateur").exists())

    def test_add_user_to_group_put_unauthorized(self):
        c = Client()

        florent = User_Profile.objects.get(username="FB1")
        c.force_login(florent)

        response = c.put("/gestion/add_user_to_group",{'username':'HSM','group_name':'Administrateur'},content_type="application/json")

        self.assertEqual(response.status_code,401)


    def test_group_list_get_authorized(self):

        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)

        c = Client()

        joran = User_Profile.objects.get(username="JoranMarie1")
        c.force_login(joran)

        response = c.get("/gestion/groups/")

        self.assertEqual(response.status_code,200)
        self.assertEqual(serializer.data, response.json())


    def test_group_list_get_unauthorized(self):

        c = Client()

        florent = User_Profile.objects.get(username="FB1")
        c.force_login(florent)

        response = c.get("/gestion/groups/")

        self.assertEqual(response.status_code,401)


    def test_group_list_post_authorized(self):

        c = Client()

        joran = User_Profile.objects.get(username="JoranMarie1")
        c.force_login(joran)

        response = c.post("/gestion/groups/",{"name":"test_group"})

        self.assertEqual(response.status_code,201)
        self.assertTrue(Group.objects.filter(name="test_group"))


    def test_group_list_post_unauthorized(self):

        c = Client()

        florent = User_Profile.objects.get(username="FB1")
        c.force_login(florent)

        response = c.post("/gestion/groups/",{"name":"test_group"})

        self.assertEqual(response.status_code,401)


    def test_group_detail_get_authorized(self):

        group = Group.objects.get(id="1")
        serializer = GroupSerializer(group)

        c = Client()

        joran = User_Profile.objects.get(username="JoranMarie1")
        c.force_login(joran)

        response = c.get("/gestion/groups/1")

        self.assertEqual(response.status_code,200)
        self.assertEqual(serializer.data, response.json())

    
    def test_group_detail_get_unauthorized(self):

        c = Client()

        florent = User_Profile.objects.get(username="FB1")
        c.force_login(florent)

        response = c.get("/gestion/groups/1")

        self.assertEqual(response.status_code,401)


    def test_group_detail_put_authorized(self):

        c = Client()

        joran = User_Profile.objects.get(username="JoranMarie1")
        c.force_login(joran)

        response = c.put("/gestion/groups/1", {"name":"new_name"}, content_type="application/json")

        group = Group.objects.get(id="1")

        self.assertEqual(response.status_code,200)
        self.assertEqual(group.name,"new_name")


    def test_group_detail_put_unauthorized(self):

        c = Client()

        florent = User_Profile.objects.get(username="FB1")
        c.force_login(florent)

        response = c.put("/gestion/groups/1", {"name":"new_name"}, content_type="application/json")

        self.assertEqual(response.status_code,401)


    def test_group_detail_delete_authorized(self):

        c = Client()

        joran = User_Profile.objects.get(username="JoranMarie1")
        c.force_login(joran)

        response = c.delete("/gestion/groups/1")

        self.assertEqual(response.status_code,204)
        self.assertFalse(Group.objects.filter(id="1").exists())


    def test_group_detail_delete_unauthorized(self):

        c = Client()

        florent = User_Profile.objects.get(username="FB1")
        c.force_login(florent)

        response = c.delete("/gestion/groups/1")

        self.assertEqual(response.status_code,401)

    
    def test_belongs_to_group_true(self):

        florent = User_Profile.objects.get(username="FB1")

        group = Group.objects.get(name="Equipe de maintenance")

        self.assertTrue(belongs_to_group(florent,group))


    def test_belongs_to_group_false(self):

        florent = User_Profile.objects.get(username="FB1")

        group = Group.objects.get(name="Administrateur")

        self.assertFalse(belongs_to_group(florent,group))