from rest_framework.response import Response
from django.contrib.auth.models import Group, Permission
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from usersmanagement.serializers import  PermissionSerializer

@api_view(['GET'])
def perms_list(request):
    """
        \n# List all permissions

        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : list all permissions and return the data
    """
    if request.method == 'GET':
        if request.user.has_perm("auth.view_permission"):
            perms = Permission.objects.all()
            serializer = PermissionSerializer(perms, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def perm_detail(request,pk):
    """
        \n# Retrieve a permission

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
    except :
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if request.user.has_perm("auth.view_permission"):
            serializer = PermissionSerializer(perm)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
