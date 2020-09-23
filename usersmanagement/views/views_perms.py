"""This module expose the permissions."""
from usersmanagement.serializers import PermissionSerializer

from django.contrib.auth.models import Permission
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class PermsList(APIView):
    """Contains HTTP method used on /usermanagement/perms/."""

    def get(self, request):
        """# List all permissions.

        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : list all permissions and return the data
        """
        if request.user.has_perm("auth.view_permission"):
            perms = Permission.objects.all()
            serializer = PermissionSerializer(perms, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class PermDetail(APIView):
    """Contains HTTP method used on /usermanagement/perms/{pk}."""

    def get(self, request, pk):
        """# Retrieve a permission.

        Parameters :
        request (HttpRequest) : the request coming from the front-end
        pk (int) : the id of the permission

        Return :
        response (Response) : the response.

        GET request : return the permission's data.

        If the user doesn't have the permissions, it will send HTTP 401.
        If the id doesn't exist, it will send HTTP 404.
        """
        try:
            perm = Permission.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("auth.view_permission"):
            serializer = PermissionSerializer(perm)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
