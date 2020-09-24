"""This module exposes our User model."""
from secrets import token_hex

from usersmanagement.models import Team, TeamType, UserProfile
from usersmanagement.serializers import (
    UserLoginSerializer,
    UserProfileSerializer,
)

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import Permission
from django.core.mail import EmailMessage
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

User = settings.AUTH_USER_MODEL


class UserList(APIView):
    """# List all users or create a new one.

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

    def get(self, request):
        """docstrings."""
        if request.user.has_perm("usersmanagement.add_userprofile"):
            users = UserProfile.objects.all()
            serializer = UserProfileSerializer(users, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        """docstrings."""
        if request.user.has_perm("usersmanagement.add_userprofile") or is_first_user():
            serializer = UserProfileSerializer(data=request.data)
            if serializer.is_valid():
                if is_first_user():
                    serializer.save()
                    init_database()
                else:
                    serializer.save()
                    send_mail_to_setup_password(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class UserDetail(APIView):
    """# Retrieve, update or delete an user.

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

    def get(self, request, pk):
        """docstrings."""
        try:
            user = UserProfile.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if (request.user == user) or (request.user.has_perm("usersmanagement.view_userprofile")):
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, pk):
        """docstrings."""
        try:
            user = UserProfile.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if (request.user == user) or (request.user.has_perm("usersmanagement.change_userprofile")):
            serializer = UserProfileSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, pk):
        """docstrings."""
        try:
            user = UserProfile.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("usersmanagement.delete_userprofile"):
            # Ici il faudra ajouter le fait qu'on ne puisse pas supprimer le dernier Administrateur
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class IsFirstUserRequest(APIView):
    """# Check if there is no user in the database.

    Parameters :
    request (HttpRequest) : the request coming from the front-end

    Return :
    response (Response) : the response

    GET request : return True or False
    """

    def get(self, request):
        """docstirngs."""
        users = UserProfile.objects.all()
        return Response(users.count() == 0)


def is_first_user():
    """
        Check, for internal needs, if there is an user in the database.
    """
    users = UserProfile.objects.all()
    return users.count() == 0


class UsernameSuffix(APIView):
    """# Tells how many users already have a specific username.

    Parameters :
    request (HttpRequest) : the request coming from the front-end

    Return :
    response (Response) : the response

    GET request : return how many users already have a specific username
        param :
            - username (String) : The username we want to check
    """

    def get(self, request):
        """docstrings."""
        username_begin = request.GET["username"]
        users = UserProfile.objects.filter(username__startswith=username_begin)
        if users.count() == 0:
            return Response("")
        else:
            return Response(str(users.count()))


@parser_classes([FormParser])
class SignIn(APIView):
    """# Sign in user if username and password are correct.

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

    def post(self, request):
        """docstring."""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'User logged in successfully',
                'token': serializer.data['token'],
                'user_id': serializer.data['user_id'],
                'user': UserProfileSerializer(UserProfile.objects.get(pk=serializer.data['user_id'])).data,
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            if str(serializer.errors.get('is_blocked')[0]) == 'True':
                send_mail_to_setup_password_after_blocking(serializer.errors.get('user_id')[0])
            response = {
                'success': 'False',
                'error': str(serializer.errors.get('error')[0]),
                'is_blocked': str(serializer.errors.get('is_blocked')[0]),
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class SignOut(APIView):
    """# Sign out the user.

    Parameters :
    request (HttpRequest) : the request coming from the front-end

    Return :
    response (Response) : Return True
    """

    def get(self, request):
        """dosctring."""
        logout(request)
        return Response(True)


class GetUserPermissions(APIView):
    """# Get all permissions of an user.

    Parameters :
    request (HttpRequest) : the request coming from the front-end
    id (int) : the id of the user

    Return :
    response (Response) : the response.

    GET request : return the user's permission.

    If the user doesn't have the permissions, it will send HTTP 401.
    If the id doesn't exist, it will send HTTP 404.
    """

    def get(self, request, pk):
        try:
            user = UserProfile.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.user.has_perm("usersmanagement.add_userprofile") or request.user == user:
            permissions = user.get_all_permissions()
            codename = []
            for perm in permissions:
                codename.append(perm.split('.')[1])
            return Response(codename)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


def send_mail_to_setup_password(data):
    """
        \n# Send an email to setup a password for a new user

        Parameters :
        data (HttpRequest) : the request coming from the front-end
    """
    user = UserProfile.objects.get(pk=data['id'])
    token = token_hex(16)
    user.set_password(token)
    user.save()
    if (settings.DEBUG is True):
        url = "https://dev.lxc.pic.brasserie-du-slalom.fr/reset-password?token=" + token + "&username=" + user.username
    else:
        url = "https://application.lxc.pic.brasserie-du-slalom.fr/reset-password?token=" + token + "&username=" + user.username

    email = EmailMessage()
    email.subject = "Set Your Password"
    email.body = "You have been invited to join openCMMS. \nTo setup your password, please follow this link : " + url
    email.to = [user.email]

    email.send()


def send_mail_to_setup_password_after_blocking(id):
    """
        \n# Send an email to setup a password for a block user

        Parameters :
        id (pk) : the id of the user who is blocked
    """
    user = UserProfile.objects.get(pk=id)
    token = token_hex(16)
    user.set_password(token)
    user.save()
    if (settings.DEBUG is True):
        url = "https://dev.lxc.pic.brasserie-du-slalom.fr/reset-password?token=" + token + "&username=" + user.username
    else:
        url = "https://application.lxc.pic.brasserie-du-slalom.fr/reset-password?token=" + token + "&username=" + user.username

    email = EmailMessage()
    email.subject = "Set Your Password"
    email.body = "You have been blocked after 3 unsuccessful login. \nTo setup your new password, please follow this link : " + url
    email.to = [user.email]

    email.send()


@api_view(['POST'])
def set_new_password(request):
    """
        \n# Set a new password for a user

        Parameters :
        request (HttpRequest) : the request coming from the front-end

        Return :
        Response (response) : the response (200 if the password is changed, 401 if the user doesn't have the permission)
    """
    token = request.data['token']
    username = request.data['username']
    password = request.data['password']
    user = UserProfile.objects.get(username=username)
    if (user.check_password(token)):
        user.set_password(password)
        user.nb_tries = 0
        user.reactivate_user()
        user.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def check_token(request):
    """
        \n# Check the token of the user

        Parameters :
        request (HttpRequest) : the request coming from the front-end

        Return :
        Response (response) : True if the token is correct else False
    """
    token = request.data['token']
    username = request.data['username']
    user = UserProfile.objects.get(username=username)
    return Response(user.check_password(token))


def init_database():

    # Creation of 3 TeamTypes
    Admins = TeamType.objects.create(name="Administrators")
    MMs = TeamType.objects.create(name="Maintenance Manager")
    MTs = TeamType.objects.create(name="Maintenance Team")

    # Creation of the 3 inital Teams
    T_Admin = Team.objects.create(name="Administrators 1", team_type=Admins)
    T_MM1 = Team.objects.create(name="Maintenance Manager 1", team_type=MMs)
    T_MT1 = Team.objects.create(name="Maintenance Team 1", team_type=MTs)

    # Adding all permissions to admins
    permis = Permission.objects.all()
    for perm in permis:
        Admins.perms.add(perm)

    Admins._apply_()
    Admins.save()
    Admins = TeamType.objects.get(name="Administrators")
    T_Admin = Admins.team_set.all()[0]

    # Adding first user to admins
    user = UserProfile.objects.all()[0]
    user.groups.add(T_Admin)
    user.save()

    T_Admin.save()
    Admins.save()
    MMs.save()
    MTs.save()

    T_Admin.save()
    T_MM1.save()
    T_MT1.save()
