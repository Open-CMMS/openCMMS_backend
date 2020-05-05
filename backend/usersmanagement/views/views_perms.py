from rest_framework.response import Response
from django.contrib.auth.models import Group, Permission
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from usersmanagement.serializers import  PermissionSerializer

@api_view(['GET'])
def perms_list(request):
    """
        List all permissions
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
        Retrieve a permission
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
