from openCMMS import settings
from usersmanagement.models import Team, UserProfile
from usersmanagement.serializers import (
    PermissionSerializer,
    UserProfileSerializer,
)
from usersmanagement.views import views_perms

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase
from rest_framework.test import APIClient

User = settings.AUTH_USER_MODEL


class permsTests(TestCase):

    def set_up(self):
        """
            Set up users and permissions for the tests
        """
        #Create permisions
        content_type = ContentType.objects.get_for_model(Team)
        permission = Permission.objects.get(codename='add_teamtype')

        #User creation
        tom = UserProfile.objects.create(
            first_name="Tom", last_name="N", email="tom.n@ac.com", password="truc", username="tn"
        )

        joe = UserProfile.objects.create(
            first_name="Joe", last_name="D", email="joe.d@ll.com", password="bouh", username="jd"
        )

        joey = UserProfile.objects.create(
            first_name="Joey",
            last_name="Bidouille",
            email="joey.bidouille@machin.com",
            password="brico",
            username="jbi"
        )

        tom.save()
        tom.user_permissions.add(permission)
        tom.save()

    def test_US1_I6_permslist_get_with_perm(self):
        """
        Test if a user with perm can retrieve all the permissions

                Inputs:
                    user (UserProfile): A UserProfile we create with the required permissions.

                Expected outputs:
                    We expect a response data which match what we expect
        """
        self.set_up()

        not_important_contenttypes = ['auth', 'admin', 'contenttypes', 'files', 'sessions', 'activity', 'entry']
        not_important_models = ['fieldvalue', 'fieldobject', 'field', 'fieldgroup', 'group', 'permissions', 'file']
        perms = Permission.objects.exclude(content_type__app_label__in=not_important_contenttypes)
        perms = perms.exclude(content_type__model__in=not_important_models)
        serializer = PermissionSerializer(perms, many=True)

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_authenticate(user=tom)

        response = c.get("/api/usersmanagement/perms/")
        self.assertEqual(serializer.data, response.json())

    def test_US1_I6_permslist_get_without_perm(self):
        """
        Test if a user with perm can't retrieve all the permissions

                Inputs:
                    user (UserProfile): A UserProfile we create without the required permissions.

                Expected outputs:
                    We expect a 401 status code in the response
        """
        self.set_up()

        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_authenticate(user=joe)

        response = c.get("/api/usersmanagement/perms/")

        self.assertEqual(response.status_code, 401)

    def test_US1_I7_permsdetails_get_with_perm(self):
        """
        Test if a user with perm can retrieve permission details

                Inputs:
                    user (UserProfile): A UserProfile we create with the required permissions.

                Expected outputs:
                    We expect a response data which match what we expect
        """
        self.set_up()

        perm = Permission.objects.get(codename="view_team")
        serializer = PermissionSerializer(perm)

        c = APIClient()

        tom = UserProfile.objects.get(username="tn")
        c.force_authenticate(user=tom)

        address = "/api/usersmanagement/perms/" + str(perm.id) + "/"

        response = c.get(address)

        self.assertEqual(serializer.data, response.data)

    def test_US1_I7_permsdetails_get_without_perm(self):
        """
        Test if a user without perm can retrieve a permission

                Inputs:
                    user (UserProfile): A UserProfile we create without the required permissions.

                Expected outputs:
                    We expect a 401 status code in the response
        """
        self.set_up()

        c = APIClient()

        joe = UserProfile.objects.get(username="jd")
        c.force_authenticate(user=joe)

        perm = Permission.objects.get(codename="view_team")

        address = "/api/usersmanagement/perms/" + str(perm.id) + "/"

        response = c.get(address)

        self.assertEqual(response.status_code, 401)
