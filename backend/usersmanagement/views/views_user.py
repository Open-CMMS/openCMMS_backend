from rest_framework.response import Response
from django.contrib.auth.models import Permission
from django.contrib.auth import authenticate,login,logout
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from usersmanagement.serializers import UserProfileSerializer
from usersmanagement.models import TeamType, UserProfile, Team

User = settings.AUTH_USER_MODEL

@api_view(['GET', 'POST'])
def user_list(request):
    """
        List all users or create a new one
    """

    if request.method == 'GET' :
        if request.user.has_perm("usersmanagement.add_UserProfile"):
            users = UserProfile.objects.all()
            serializer = UserProfileSerializer(users, many=True)
            return Response(serializer.data)
        else :
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'POST' :
        if request.user.has_perm("usersmanagement.add_UserProfile") or is_first_user():
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
    try:
        user = UserProfile.objects.get(pk=pk)
    except :
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if (request.user == user) or (request.user.has_perm("usersmanagement.view_UserProfile")):
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)
        else :
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'PUT':
        if (request.user == user) or (request.user.has_perm("usersmanagement.change_UserProfile")):
            serializer = UserProfileSerializer(user, data = request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else :
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'DELETE':
        if (request.user.has_perm("usersmanagement.delete_UserProfile")):
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
    username = request.data.get("username",None)
    password = request.data.get("password",None)
    user = UserProfile.objects.get(username=username)
    if user.is_active :
        user = authenticate(username=username, password=password)
        if user is not None:
            user.nb_tries = 0
            user.save()
            login(request, user)
            return Response((True, False, user.pk))
        user = UserProfile.objects.get(username=username)
        user.nb_tries+=1
        if user.nb_tries == 3 :
            user.deactivate_user()
            user.save()
            return Response((False, True, 0))
        user.save()
        return Response((False, False, 0))
    else :
        return Response(status=status.HTTP_401_UNAUTHORIZED)

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

    Admins.apply()

    #Adding first user to admins
    user = UserProfile.objects.all()[0]
    user.groups.add(T_Admin)
