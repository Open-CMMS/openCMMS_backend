from rest_framework.response import Response
from django.contrib.auth.models import Group, Permission
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from usersmanagement.serializers import  PermissionSerializer
from django.contrib.auth import authenticate, login, logout

User = settings.AUTH_USER_MODEL

@api_view(['GET', 'POST'])
def perms_list(request):
    """
        List all permissions or create a new one
    """

    user = authenticate(username='user', password='pass')
    login(request, user)

    if request.method == 'GET':
        if request.user.has_perm("auth.view_permission"):
            perms = Permission.objects.all()
            serializer = PermissionSerializer(perms, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        if request.user.has_perm("auth.add_permission"):
            serializer = PermissionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET','PUT','DELETE'])
def perm_detail(request,pk):
    """
        Retrieve, update or delete a permission
    """
    user = authenticate(username='user', password='pass')
    login(request, user)

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

    elif request.method == 'PUT':
        if request.user.has_perm("auth.change_permission"):
            serializer = PermissionSerializer(perm, data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


    elif request.method == 'DELETE':
        if request.user.has_perm("auth.delete_permission"):
            perm.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
