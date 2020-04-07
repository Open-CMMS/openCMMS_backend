from rest_framework.response import Response
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import authenticate,login,logout
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from usersmanagement.serializers import UserProfileSerializer, TeamSerializer, PermissionSerializer, GroupTypeSerializer
from usersmanagement.models import GroupType, UserProfile, Team


User = settings.AUTH_USER_MODEL


@api_view(['GET', 'POST'])
def group_list(request):
    """
        List all groups or create a new one
    """
    if request.user.has_perm("auth.view_group"):
        if request.method == 'GET':
            groups = Group.objects.all()
            serializer = GroupSerializer(groups, many=True)
            return Response(serializer.data)
        
    if request.user.has_perm("auth.add_group"):
        if request.method == 'POST' :
            serializer = GroupSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_401_UNAUTHORIZED)




@api_view(['GET', 'PUT', 'DELETE'])
def group_detail(request, pk):
    """
        Retrieve, update or delete a group
    """
    try:
        group = Group.objects.get(pk=pk)
    except :
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if request.user.has_perm("auth.view_group"):
            serializer = GroupSerializer(group)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'PUT':
        if request.user.has_perm("auth.change_group"):
            serializer = GroupSerializer(group, data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'DELETE':
        if request.user.has_perm("auth.delete_group"):
            group.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)




@api_view(['POST', 'PUT'])
def add_user_to_group(request):
    """
        Add and remove users from groups
    """

    if request.user.has_perm("auth.change_group"):
        if request.method == 'POST':
            user = User_Profile.objects.get(username=request.data["username"])
            group = Group.objects.get(name=request.data["group_name"])
            group.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)


        elif request.method == 'PUT':
            user = User_Profile.objects.get(username=request.data["username"])
            group = Group.objects.get(name=request.data["group_name"])
            group.user_set.remove(user)
            return Response(status=status.HTTP_201_CREATED)
    
    return Response(status=status.HTTP_401_UNAUTHORIZED)



def belongs_to_group(user, group):
    return user.groups.filter(id=group.id).exists()
