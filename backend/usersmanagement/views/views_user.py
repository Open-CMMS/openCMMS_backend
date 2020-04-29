from rest_framework.response import Response
from django.contrib.auth.models import Permission
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from usersmanagement.serializers import UserProfileSerializer, UserLoginSerializer
from usersmanagement.models import TeamType, UserProfile, Team

User = settings.AUTH_USER_MODEL

@api_view(['GET', 'POST'])
def user_list(request):
    """
        List all users or create a new one
    """

    user = authenticate(username='user', password='pass')
    login(request, user)
    if request.method == 'GET' :
        if request.user.has_perm("usersmanagement.add_userprofile"):
            users = UserProfile.objects.all()
            serializer = UserProfileSerializer(users, many=True)
            return Response(serializer.data)
        else :
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'POST' :
        if request.user.has_perm("usersmanagement.add_userprofile") or is_first_user():
            serializer = UserProfileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                if is_first_user():
                    init_database()
                    user = UserProfile.objects.all()[0]
                    login(request, user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else :
            return Response(status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    """
        Retrieve, update or delete an user account
    """
    user = authenticate(username='user', password='pass')
    login(request, user)
    
    try:
        user = UserProfile.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if (request.user == user) or (request.user.has_perm("usersmanagement.view_userprofile")):
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)
        else :
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'PUT':
        if (request.user == user) or (request.user.has_perm("usersmanagement.change_userprofile")):
            serializer = UserProfileSerializer(user, data = request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else :
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'DELETE':
        if request.user.has_perm("usersmanagement.delete_userprofile"):
            #Ici il faudra ajouter le fait qu'on ne puisse pas supprimer le dernier Administrateur
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else :
            return Response(status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET'])
def is_first_user_request(request):
    """
        Return True if there is no user in the database
    """
    if request.method == 'GET':
        users = UserProfile.objects.all()
        return Response(users.count() == 0)

def is_first_user():
    users = UserProfile.objects.all()
    return users.count() == 0


@api_view(['GET'])
def username_suffix(request):
    """
        Return the suffix to append to the username
    """
    if request.method == 'GET':
        username_begin = request.GET["username"]
        users = UserProfile.objects.filter(username__startswith = username_begin)
        if users.count()==0:
            return Response("")
        else :
            return Response (str(users.count()))



@api_view(['POST'])
def sign_in(request):
    """
        Sign in the user if the password and the login are correct
    """
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    response = {
        'success' : 'True',
        'status code' : status.HTTP_200_OK,
        'message' : 'User logged in successfully',
        'token' : serializer.data['token'],
        'user_id' : serializer.data['user_id'],
    }
    return Response(response, status=status.HTTP_200_OK)

@api_view(['GET'])
def sign_out(request):
    """
        Sign out the user
    """
    logout(request)
    return Response(True)


def init_database():

    #Creation of 3 TeamTypes
    Admins = TeamType.objects.create(name="Administrators")
    MMs = TeamType.objects.create(name="Maintenance Manager")
    MTs = TeamType.objects.create(name="Maintenance Team")

    #Creation of the 3 inital Teams
    T_Admin = Team.objects.create(name="Administrators 1", team_type=Admins)
    T_MM1 = Team.objects.create(name="Maintenance Manager 1", team_type=MMs)
    T_MT1 = Team.objects.create(name="Maintenance Team 1", team_type=MTs)

    #Adding all permissions to admins
    perms = Permission.objects.all()
    for perm in perms:
        Admins.perms.add(perm)

    Admins._apply_()

    #Adding first user to admins
    user = UserProfile.objects.all()[0]
    user.groups.add(T_Admin)
