from usersmanagement.models import UserProfile
from usersmanagement.serializers import UserProfileSerializer
from django.test import TestCase, RequestFactory, Client
from usersmanagement.views.views_user import is_first_user

class UserTests(TestCase):

    def set_up(self,active):
        """
            Set up a user, active or not
        """
        user = UserProfile(username='tom')
        user.set_password('truc')
        user.is_active = active
        user.save()
        return user

    def set_up_field(self,field,value):
        user = UserProfile(username='tom', **{field : value})
        user.set_password('truc')
        user.save()
        return user

    def set_up_update_test(self,user, field,value):
        """
            Set up an update of a user and its test
        """
        user.field = 'value'
        user.save()
        self.assertEqual(user.field,'value')

    def test_username_create(self):
        """
            Test the creation of a user with its username
        """
        user = UserProfile(username='tom')
        user.save()
        self.assertEqual(user.username,"tom")

    def test_username_update(self):
        """
            Test the modification of a user's username
        """
        user = self.set_up(True)
        self.set_up_update_test(user,'username','joe')

    def test_first_name_create(self):
         """
             Test the creation of a user with its first name
         """
         user = self.set_up_field("first_name","tom")
         self.assertEqual(user.first_name,"tom")

    def test_first_name_update(self):
        """
            Test the modification of a user's first name
        """
        user = self.set_up_field('first_name','tom')
        self.set_up_update_test(user,'first_name','joe')

    def test_last_name_create(self):
         """
             Test the creation of a user with its last name
         """
         user = self.set_up_field("last_name","tom")
         self.assertEqual(user.last_name,"tom")

    def test_last_name_update(self):
        """
            Test the modification of a user's last name
        """
        user = self.set_up_field('last_name','tom')
        self.set_up_update_test(user,'last_name','joe')

    def test_email_create(self):
         """
             Test the creation of a user with its last name
         """
         user = self.set_up_field("email","tom@tom.com")
         self.assertEqual(user.email,"tom@tom.com")

    def test_email_update(self):
        """
            Test the modification of a user's email
        """
        user = self.set_up_field('email','tom@tom.com')
        self.set_up_update_test(user,'email','joe@joe.com')

    def test_nb_tries_create(self):
         """
             Test the creation of a user with its nb tries
         """
         user = self.set_up_field("nb_tries","0")
         self.assertEqual(user.nb_tries,"0")

    def test_nb_tries_update(self):
        """
            Test the modification of a user's nb tries
        """
        user = self.set_up_field('nb_tries','0')
        self.set_up_update_test(user,'nb_tries','1')

    def test_is_active_create(self):
         """
             Test the creation of a user with its nb tries
         """
         user = self.set_up_field("is_active","True")
         self.assertEqual(user.is_active,"True")

    def test_is_active_update(self):
        """
            Test the modification of a user's nb tries
        """
        user = self.set_up_field('is_active','True')
        self.set_up_update_test(user,'is_active','False')

    def test_is_first_user_with_first_user(self):
        """
            Test is_first_user with the first user
        """
        result = is_first_user()
        self.assertEqual(result,True)

    def test_is_first_user_without_first_user(self):
        """
            Test is_first_user without the first user
        """
        self.set_up(True)
        result = is_first_user()
        self.assertEqual(result,False)

    def test_deactivate_user_active(self):
        """
            Test the deactivation of a user if it's active
        """
        user = self.set_up(True)
        user.deactivate_user()
        self.assertEqual(user.is_active , False)

    def test_activate_user_active(self):
        """
            Test the activation of a user if it's active
        """
        user = self.set_up(True)
        user.reactivate_user()
        self.assertEqual(user.is_active , True)

    def test_deactivate_user_unactive(self):
        """
            Test the deactivation of a user if it's unactive
        """
        user = self.set_up(False)
        user.deactivate_user()
        self.assertEqual(user.is_active , False)

    def test_activate_user_unactive(self):
        """
            Test the activation of a user if it's unactive
        """
        user = self.set_up(False)
        user.reactivate_user()
        self.assertEqual(user.is_active , True)