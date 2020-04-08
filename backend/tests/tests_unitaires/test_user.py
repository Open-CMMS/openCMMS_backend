from usersmanagement.models import UserProfile
from django.test import TestCase

class UserTests(TestCase):

    def set_up(self,active):
        user = UserProfile(username='tom')
        user.set_password('truc')
        user.is_active = active
        user.save()
        return user

    def test_deactivate_user_active(self):
        user = self.set_up(True)
        user.deactivate_user()
        self.assertEqual(user.is_active , False)

    def test_activate_user_active(self):
        user = self.set_up(True)
        user.reactivate_user()
        self.assertEqual(user.is_active , True)

    def test_deactivate_user_unactive(self):
        user = self.set_up(False)
        user.deactivate_user()
        self.assertEqual(user.is_active , False)

    def test_activate_user_unactive(self):
        user = self.set_up(False)
        user.reactivate_user()
        self.assertEqual(user.is_active , True)
