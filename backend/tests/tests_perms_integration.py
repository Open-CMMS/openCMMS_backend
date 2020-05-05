from django.test import TestCase, RequestFactory
from rest_framework.test import APIClient
from usersmanagement.models import UserProfile, Team
from django.contrib.auth.models import Permission
from usersmanagement.views import views_perms
from usersmanagement.serializers import UserProfileSerializer, PermissionSerializer
from django.contrib.contenttypes.models import ContentType
from openCMMS import settings

User = settings.AUTH_USER_MODEL

class permsTests(TestCase):

    def set_up(self):
        #Create permisions
        content_type = ContentType.objects.get_for_model(Team)
        permission = Permission.objects.get(codename='add_permission')
        permission2 = Permission.objects.get(codename='view_permission')
        permission3 = Permission.objects.get(codename='delete_permission')
        permission4 = Permission.objects.get(codename='change_permission')

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

        tom.save()
        tom.user_permissions.add(permission)
        tom.user_permissions.add(permission2)
        tom.user_permissions.add(permission3)
        tom.user_permissions.add(permission4)
        tom.save()

    def test_perms_list_get_authorized(self):
        self.set_up()

        perms = Permission.objects.all()
        serializer = PermissionSerializer(perms, many=True)

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_authenticate(user=tom)

        response = c.get("/api/usersmanagement/perms/")
        self.assertEqual(serializer.data, response.json())


    def test_perm_list_get_unauthorized(self):
        self.set_up()

        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_authenticate(user=joe)

        response = c.get("/api/usersmanagement/perms/")

        self.assertEqual(response.status_code,401)


    def test_perm_list_post_authorized(self):
        self.set_up()

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_authenticate(user=tom)

        response = c.post("/api/usersmanagement/perms/",{"name":"test_perm","codename":"test", "content_type" : ContentType.objects.get_for_model(Team)})
        perm = Permission.objects.get(pk=response.data['id'])
        self.assertEqual(response.status_code,201)
        self.assertTrue(perm.objects.filter(name="test_perm"))

    def test_perm_list_post_unauthorized(self):
        self.set_up()

        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_authenticate(user=joe)

        response = c.post("/api/usersmanagement/perms/",{"name":"test_perm"})

        self.assertEqual(response.status_code,401)


    def test_perm_detail_get_authorized(self):
        self.set_up()

        perm = Permission.objects.get(codename="view_permission")
        serializer = PermissionSerializer(perm)

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_authenticate(user=tom)

        address = "/api/usersmanagement/perms/"+str(perm.id)+"/"

        response = c.get(address)

        self.assertEqual(serializer.data, response.data)


    def test_perm_detail_get_unauthorized(self):
        self.set_up()

        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_authenticate(user=joe)

        perm = Permission.objects.get(codename="view_permission")

        address = "/api/usersmanagement/perms/"+str(perm.id)+"/"

        response = c.get(address)

        self.assertEqual(response.status_code,401)


    def test_perm_detail_put_change_name_authorized(self):
        self.set_up()

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_authenticate(user=tom)

        perm = Permission.objects.get(codename="view_permission")
        address = "/api/usersmanagement/perms/"+str(perm.id)+"/"

        response = c.put(address,{"name":"new_name"}, format='json')

        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['name'],"new_name")

    def test_perm_detail_put_unauthorized(self):
        self.set_up()

        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_authenticate(user=joe)

        perm = Permission.objects.get(codename="view_permission")

        address = "/api/usersmanagement/perms/"+str(perm.id)+"/"

        response = c.put(address, {"name":"new_name"}, content_type="application/json")

        self.assertEqual(response.status_code,401)


    def test_perm_detail_delete_authorized(self):
        self.set_up()

        c = APIClient()
        perm = Permission.objects.get(codename="view_permission")

        tom = UserProfile.objects.get(username="tn")
        c.force_authenticate(user=tom)

        address = "/api/usersmanagement/perms/"+str(perm.id)+"/"

        response = c.delete(address)

        self.assertEqual(response.status_code,204)
        with self.assertRaises(perm.DoesNotExist):
            perm_final = Permission.objects.get(codename="view_permission")


    def test_perm_detail_delete_unauthorized(self):
        self.set_up()

        c = APIClient()
        perm = Permission.objects.get(codename="view_permission")

        joe = UserProfile.objects.get(username="jd")
        c.force_authenticate(user=joe)

        address = "/api/usersmanagement/perms/"+str(perm.id)+"/"

        response = c.delete(address)

        self.assertEqual(response.status_code,401)
