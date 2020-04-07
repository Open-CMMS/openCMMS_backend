from rest_framework.response import Response
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import authenticate,login,logout
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from usersmanagement.serializers import UserProfileSerializer, TeamSerializer, PermissionSerializer, GroupTypeSerializer
from usersmanagement.models import GroupType, UserProfile

User = settings.AUTH_USER_MODEL

@api_view(['GET','POST'])
def grouptypes_list(request):
    """
        List all the group types
    """

    if request.method == 'GET':
        if request.user.has_perm("gestion.view_grouptype"):
            group_types = GroupType.objects.all()
            serializer = GroupTypeSerializer(group_types, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        if request.user.has_perm("gestion.add_grouptype"):
            serializer = GroupTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'PUT', 'DELETE'])
def grouptypes_detail(request,pk):
    """
        Retrieve, update or delete a GroupType
    """

    try:
        group_type = GroupType.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if request.user.has_perm("gestion.view_grouptype"):
            serializer = GroupTypeSerializer(group_type)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'PUT':
        if request.user.has_perm("gestion.change_grouptype"):
            serializer = GroupTypeSerializer(group_type, data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'DELETE':
        if request.user.has_perm("gestion.delete_grouptype"):
            group_type.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
