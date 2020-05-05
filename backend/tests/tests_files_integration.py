from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission 
from django.test import TestCase, Client
from rest_framework.test import APIClient
from usersmanagement.models import UserProfile
from maintenancemanagement.models import File
from maintenancemanagement.serializers import FileSerializer

class FileTests(TestCase):

    def set_up_perm(self):
        """
            Set up a user with permissions
        """
        permission = Permission.objects.get(codename='add_file')
        permission2 = Permission.objects.get(codename='view_file')  
        permission3 = Permission.objects.get(codename='delete_file')
        permission4 = Permission.objects.get(codename='change_file')                             
        
        user = UserProfile.objects.create(username='tom')
        user.set_password('truc')
        user.first_name='Tom'
        user.save()
        
        user.user_permissions.add(permission)
        user.user_permissions.add(permission2)
        user.user_permissions.add(permission3)
        user.user_permissions.add(permission4)
        
        user.save()
        return user

    def set_up_without_perm(self):
        """
            Set up a user without permissions
        """
        user = UserProfile.objects.create(username='tom')
        user.set_password('truc')
        user.first_name='Tom'
        user.save()
        return user
    
    