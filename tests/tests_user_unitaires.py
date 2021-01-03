from usersmanagement.models import UserProfile
from usersmanagement.serializers import UserProfileSerializer
from usersmanagement.views.views_user import init_database, is_first_user

from django.test import Client, RequestFactory, TestCase


class UserTests(TestCase):

    def set_up(self, active):
        """
            Set up a user, active or not
        """
        user = UserProfile(username='tom')
        user.set_password('truc')
        user.is_active = active
        user.save()
        return user

    def set_up_field(self, field, value):
        user = UserProfile(username='tom', **{field: value})
        user.set_password('truc')
        user.save()
        return user

    def set_up_update_test(self, user, field, value):
        """
            Set up an update of a user and its test
        """
        user.field = 'value'
        user.save()
        self.assertEqual(user.field, 'value')

    def test_US2_U1_username_create(self):
        """
            Test if we can create an user with an username

            Inputs:
                username (string): the username to verify

            Expected Output:
                We expect that the user has been created in the database
        """
        user = UserProfile(username='tom')
        user.save()
        self.assertEqual(user.username, "tom")

    def test_US2_U1_username_update(self):
        """
            Test if we can update an user's username

            Inputs:
                username (string): the username to update

            Expected Output:
                We expect that the user has been updated in the database
        """
        user = self.set_up(True)
        self.set_up_update_test(user, 'username', 'joe')

    def test_US2_U1_first_name_create(self):
        """
            Test if we can create an user with a first name

            Inputs:
                first_name (string): the firstname to verify

            Expected Output:
                We expect that the user has been created in the database
        """
        user = self.set_up_field("first_name", "tom")
        self.assertEqual(user.first_name, "tom")

    def test_US2_U1_first_name_update(self):
        """
            Test if we can update an user's first name

            Inputs:
                first_name (string): the first_name to update

            Expected Output:
                We expect that the user has been updated in the database
        """
        user = self.set_up_field('first_name', 'tom')
        self.set_up_update_test(user, 'first_name', 'joe')

    def test_US2_U1_last_name_create(self):
        """
            Test if we can create an user with a last name

            Inputs:
                last_name (string): the lastname to verify

            Expected Output:
                We expect that the user has been created in the database
        """
        user = self.set_up_field("last_name", "tom")
        self.assertEqual(user.last_name, "tom")

    def test_US2_U1_last_name_update(self):
        """
            Test if we can update an user's last name

            Inputs:
                last_name (string): the last_name to update

            Expected Output:
                We expect that the user has been updated in the database
        """
        user = self.set_up_field('last_name', 'tom')
        self.set_up_update_test(user, 'last_name', 'joe')

    def test_US2_U1_email_create(self):
        """
            Test if we can create an user with an email

            Inputs:
                email (string): the email to verify

            Expected Output:
                We expect that the user has been created in the database
        """
        user = self.set_up_field("email", "tom@tom.com")
        self.assertEqual(user.email, "tom@tom.com")

    def test_US2_U1_email_update(self):
        """
            Test if we can update an user's email

            Inputs:
                email (string): the email to update

            Expected Output:
                We expect that the user has been updated in the database
        """
        user = self.set_up_field('email', 'tom@tom.com')
        self.set_up_update_test(user, 'email', 'joe@joe.com')

    def test_US2_U1_nb_tries_create(self):
        """
            Test if we can create an user with nb_tries

            Inputs:
                nb_tries (string): the nb_tries to verify

            Expected Output:
                We expect that the user has been created in the database
        """
        user = self.set_up_field("nb_tries", "0")
        self.assertEqual(user.nb_tries, "0")

    def test_US2_U1_nb_tries_update(self):
        """
            Test if we can update an user's nb_tries

            Inputs:
                nb_tries (string): the nb_tries to update

            Expected Output:
                We expect that the user has been updated in the database
        """
        user = self.set_up_field('nb_tries', '0')
        self.set_up_update_test(user, 'nb_tries', '1')

    def test_US2_U1_is_active_create(self):
        """
            Test if we can create an user with is_active

            Inputs:
                is_active (string): the is_active to verify

            Expected Output:
                We expect that the user has been created in the database
        """
        user = self.set_up_field("is_active", "True")
        self.assertEqual(user.is_active, "True")

    def test_US2_U1_is_active_update(self):
        """
            Test if we can update an user's is_active

            Inputs:
                is_active (string): the is_active to update

            Expected Output:
                We expect that the user has been updated in the database
        """
        user = self.set_up_field('is_active', 'True')
        self.set_up_update_test(user, 'is_active', 'False')

    def test_US2_U2_is_first_user_with_first_user(self):
        """
            Test if is_first_user returns the correct result

            Inputs:
                None

            Expected Output:
                We expect that function returns True as there is no user in the database
        """
        result = is_first_user()
        self.assertEqual(result, True)

    def test_US2_U2_is_first_user_without_first_user(self):
        """
            Test if is_first_user returns the correct result

            Inputs:
                None

            Expected Output:
                We expect that function returns False as there is an user in the database
        """
        self.set_up(True)
        result = is_first_user()
        self.assertEqual(result, False)

    def test_US2_U3_deactivate_user_active(self):
        """
            Test if deactivate_user works well

            Inputs:
                user (UserProfile) : an active user

            Expected Output:
                We expect that the user has been deactivated
        """
        user = self.set_up(True)
        user.deactivate_user()
        self.assertEqual(user.is_active, False)

    def test_US2_U3_deactivate_user_unactive(self):
        """
            Test if deactivate_user works well

            Inputs:
                user (UserProfile) : an inactive user

            Expected Output:
                We expect that the user remains deactivated
        """
        user = self.set_up(False)
        user.deactivate_user()
        self.assertEqual(user.is_active, False)

    def test_US2_U4_activate_user_active(self):
        """
            Test if reactivate_user works well

            Inputs:
                user (UserProfile) : an active user

            Expected Output:
                We expect that the user remains activated
        """
        user = self.set_up(True)
        user.reactivate_user()
        self.assertEqual(user.is_active, True)

    def test_US2_U4_activate_user_unactive(self):
        """
            Test if reactivate_user works well

            Inputs:
                user (UserProfile) : an inactive user

            Expected Output:
                We expect that the user becomes activated
        """
        user = self.set_up(False)
        user.reactivate_user()
        self.assertEqual(user.is_active, True)
