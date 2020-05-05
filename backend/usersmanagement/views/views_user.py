from rest_framework.response import Response
from django.contrib.auth.models import Permission
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from usersmanagement.serializers import UserProfileSerializer, UserLoginSerializer, PermissionSerializer
from usersmanagement.models import TeamType, UserProfile, Team

User = settings.AUTH_USER_MODEL

@api_view(['GET', 'POST'])
def user_list(request):
    """
        \n# List all users or create a new one

        
        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : list all users and return the data
        POST request : 
        - create a new user, send HTTP 201.  If the request is not valid, send HTTP 400.
        - If the user doesn't have the permissions, it will send HTTP 401.
        - The request must contain username (the username of the user (String)) and password (password of the user (String))
        - The request can also contain :
            - first_name (String): User first name
            - last_name (String): User last name
            - email (String):user mail
    """

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
        \n# Retrieve, update or delete an user

        Parameters :
        request (HttpRequest) : the request coming from the front-end
        id (int) : the id of the user

        Return :
        response (Response) : the response.

        GET request : return the user's data.
        PUT request : change the user with the data on the request or if the data isn't well formed, send HTTP 400.
        DELETE request: delete the tasktype and send HTTP 204.

        If the user doesn't have the permissions, it will send HTTP 401.
        If the id doesn't exist, it will send HTTP 404.

        The PUT request can contain one or more of the following fields : 
            - first_name (String): User first_name
            - last_name (String):user last_name
            - email (String): user mail
            - password (String) : user password

        Warning ! You can't change the username !
    """
    
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
        \n# Check if there is no user in the database

        Parameters :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response

        GET request : return True or False
    """
    if request.method == 'GET':
        users = UserProfile.objects.all()
        return Response(users.count() == 0)

def is_first_user():
    """
        Check, for internal needs, if there is an user in the database.
    """
    users = UserProfile.objects.all()
    return users.count() == 0


@api_view(['GET'])
def username_suffix(request):
    """
        \n# Tells how many users already have a specific username

        Parameters :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response

        GET request : return how many users already have a specific username
            param : 
                - username (String) : The username we want to check
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
        \n# Sign in user if username and password are correct

        Parameters :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response

        POST request : 
            param : 
                - username (String) : The username we want to sign in
                - password (String) : The password entered by user
            response params :
                - successs : True or False
                - token : The JWT Token
                - user_id : The user id
                - user : All the informations about the user
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
        \n# Sign out the user

        Parameters :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : Return True
    """
    logout(request)
    return Response(True)


@api_view(['GET'])
def get_user_permissions(request, pk):
    """
        \n# Get all permissions of an user

        Parameters :
        request (HttpRequest) : the request coming from the front-end
        id (int) : the id of the user

        Return :
        response (Response) : the response.

        GET request : return the user's permission.
        
        If the user doesn't have the permissions, it will send HTTP 401.
        If the id doesn't exist, it will send HTTP 404.

    """

    try :
        user = UserProfile.objects.get(pk=pk)
    except :
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.user.has_perm("usersmanagement.add_userprofile"):
        permissions = user.user_permissions
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


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
