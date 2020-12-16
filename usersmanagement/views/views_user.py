"""This module defines the views corresponding to users."""

import logging
from secrets import token_hex

from drf_yasg.utils import swagger_auto_schema

from django.conf import settings
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import Permission
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from usersmanagement.models import Team, TeamType, UserProfile
from usersmanagement.serializers import (
    UserLoginSerializer,
    UserProfileSerializer,
)
from utils.init_db import initialize_db

logger = logging.getLogger(__name__)

User = settings.AUTH_USER_MODEL

ADD_USERPROFILE = "usersmanagement.add_userprofile"
VIEW_USERPROFILE = "usersmanagement.view_userprofile"
CHANGE_USERPROFILE = "usersmanagement.change_userprofile"
DELETE_USERPROFILE = "usersmanagement.delete_userprofile"

MAIL_ERROR = "There was an exception while sending a mail.\n{}"


class UserList(APIView):
    """# List all users or create a new one.

    Parameter :
    request (HttpRequest) : the request coming from the front-end

    Return :
    response (Response) : the response.

    GET request : list all users and return the data
    POST request :
    - create a new user, send HTTP 201.  If the request is not valid, \
        send HTTP 400.
    - If the user doesn't have the permissions, it will send HTTP 401.
    - The request must contain username (the username of the user (String))\
         and password (password of the user (String))
    - The request can also contain :
        - first_name (String): User first name
        - last_name (String): User last name
        - email (String):user mail
    """

    @swagger_auto_schema(
        operation_description="Send the list of user in database.",
        responses={
            200: "Send back the list.",
            401: "The client was not authorized to see the ressource."
        }
    )
    def get(self, request):
        """docstrings."""
        if request.user.has_perm(VIEW_USERPROFILE):
            users = UserProfile.objects.all()
            serializer = UserProfileSerializer(users, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        query_serializer=UserProfileSerializer,
        operation_description="Create a new user in database.",
        responses={
            201: "Send back the data and the user was created.",
            400: "The request contained bad data.",
            401: "The client was not authorized to see the ressource."
        }
    )
    def post(self, request):
        """docstrings."""
        if request.user.has_perm(ADD_USERPROFILE) or is_first_user():
            serializer = UserProfileSerializer(data=request.data)
            if serializer.is_valid():
                if is_first_user():
                    serializer.save()
                    initialize_db()
                else:
                    serializer.save()
                    send_mail_to_setup_password(serializer.data)
                logger.info("{user} CREATED User with {params}".format(user=request.user, params=request.data))
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
    PUT request : change the user with the data on the request or if\
         the data isn't well formed, send HTTP 400.
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

    @swagger_auto_schema(
        query_serializer=UserProfileSerializer,
        operation_description="Send back the sata of a user from database.",
        responses={
            200: "Send the data asked",
            401: "The client was not authorized to see the ressource.",
            404: "The user was not found in the database.",
        }
    )
    def get(self, request, pk):
        """docstrings."""
        try:
            user = UserProfile.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if (request.user == user) or (request.user.has_perm(VIEW_USERPROFILE)):
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        query_serializer=UserProfileSerializer,
        operation_description="Update a user from database.",
        responses={
            200: "Send the data asked",
            400: "The client sent bad data",
            401: "The client was not authorized to update the ressource.",
            404: "The user was not found in the database.",
        }
    )
    def put(self, request, pk):
        """docstrings."""
        try:
            user = UserProfile.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if (request.user == user) or (request.user.has_perm(CHANGE_USERPROFILE)):
            serializer = UserProfileSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                logger.info(
                    "{user} UPDATED {object} with {params}".format(
                        user=request.user, object=repr(user), params=request.data
                    )
                )
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        query_serializer=UserProfileSerializer,
        operation_description="Delete a user from database.",
        responses={
            204: "The user was deleted from database.",
            401: "The user was not found in the database.",
            404: "The user was not found"
        }
    )
    def delete(self, request, pk):
        """docstrings."""
        try:
            user = UserProfile.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm(DELETE_USERPROFILE):
            # Ici il faudra ajouter le fait qu'on ne puisse pas supprimer
            #  le dernier Administrateur
            logger.info("{user} DELETED {object}".format(user=request.user, object=repr(user)))
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

    @swagger_auto_schema(operation_description="Send True if the database contains no user, send False otherwise.")
    def get(self, request):
        """docstirngs."""
        users = UserProfile.objects.all()
        return Response(users.count() == 0)


def is_first_user():
    """Check, for internal needs, if there is an user in the database."""
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

    @swagger_auto_schema(
        operation_description="Send the number of users",
    )
    def get(self, request):
        """docstrings."""
        username_begin = request.GET["username"]
        users = UserProfile.objects.filter(username__startswith=username_begin)
        if users.count() == 0:
            return Response("")
        else:
            return Response(str(users.count()))


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

    @swagger_auto_schema(
        operation_description="Login a client.",
        responses={
            200: 'The request went well.',
            400: 'The login were incorrect.'
        }
    )
    def post(self, request):
        """docstring."""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            if UserProfile.objects.get(username=request.data['username']).groups.count() == 0:
                error = {
                    'success': 'False',
                    'error': 'User has no team',
                }
                response = {'error': error}
            else:
                data = {
                    'success': 'True',
                    'status code': status.HTTP_200_OK,
                    'message': 'User logged in successfully',
                    'token': serializer.data['token'],
                    'user_id': serializer.data['user_id'],
                    'user': UserProfileSerializer(UserProfile.objects.get(pk=serializer.data['user_id'])).data,
                }
                response = {'data': data}
        else:
            if str(serializer.errors.get('is_blocked')[0]) == 'True':
                send_mail_to_setup_password_after_blocking(serializer.errors.get('user_id')[0])
            error = {
                'success': 'False',
                'error': str(serializer.errors.get('error')[0]),
                'is_blocked': str(serializer.errors.get('is_blocked')[0]),
            }
            response = {'error': error}
        return Response(response, status=status.HTTP_200_OK)  # Do not change this error code


class SignOut(APIView):
    """# Sign out the user.

    Parameters :
    request (HttpRequest) : the request coming from the front-end

    Return :
    response (Response) : Return True
    """

    @swagger_auto_schema(operation_description='Log out the client.', responses={200: 'The request went well.'})
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

    @swagger_auto_schema(
        operation_description='Send the authorization of the user.',
        responses={
            200: 'The request went well.',
            401: 'The client was not authorized to see the permissions of the user.',
            404: 'The user was not found.'
        }
    )
    def get(self, request, pk):
        """Send the authorization of the user."""
        try:
            user = UserProfile.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.user.has_perm(ADD_USERPROFILE) or request.user == user:
            permissions = user.get_all_permissions()
            codename = []
            for perm in permissions:
                codename.append(perm.split('.')[1])
            return Response(codename)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


def send_mail_to_setup_password(data):
    """# Send an email to setup a password for a new user.

    Parameters :
    data (HttpRequest) : the request coming from the front-end
    """
    user = UserProfile.objects.get(pk=data['id'])
    token = token_hex(16)
    user.set_password(token)
    user.save()
    url = f"{settings.BASE_URL}reset-password?token={token}&username={user.username}"
    email = EmailMessage()
    email.subject = "Set Your Password"
    email.body = f"You have been invited to join openCMMS. \nTo setup your password, please follow this link : {url}"
    email.to = [user.email]

    try:
        email.send()
    except Exception as e:
        logger.warning(MAIL_ERROR, e)


def send_mail_to_setup_password_after_blocking(id):
    """# Send an email to setup a password for a block user.

    Parameters :
    id (pk) : the id of the user who is blocked
    """
    user = UserProfile.objects.get(pk=id)
    token = token_hex(16)
    user.set_password(token)
    user.save()
    url = f"{settings.BASE_URL}reset-password?token={token}&username={user.username}"
    email = EmailMessage()
    email.subject = "Set Your Password"
    email.body = f"You have been blocked after 3 unsuccessful login.\
To setup your new password, please follow this link : {url}"

    email.to = [user.email]

    try:
        email.send()
    except Exception as e:
        logger.warning(MAIL_ERROR, e)


class SetNewPassword(APIView):
    """# Set a new password for a user.

    Parameters :
    request (HttpRequest) : the request coming from the front-end

    Return :
    Response (response) : the response (200 if the password is changed,\
         401 if the user doesn't have the permission)
    """

    @swagger_auto_schema(
        operation_description='Change the password of the user.',
        responses={
            200: 'The request went well.',
            401: 'The client was not authorized to change the password of the user.'
        }
    )
    def post(self, request):
        """docstrings."""
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


class UserResetPassword(APIView):
    """The APIView class to reset a password."""

    def get(self, request):
        """Reset the password."""
        email = request.GET.get('email', "")
        username = request.GET.get('username', "")
        user1 = UserProfile.objects.filter(email=email)
        user2 = UserProfile.objects.filter(username=username)
        user = user1 | user2
        if user.count() == 0:
            return Response("User not found", status=status.HTTP_400_BAD_REQUEST)
        user = user[0]
        token = token_hex(16)
        user.set_password(token)
        user.save()
        url = f"{settings.BASE_URL}reset-password?token={token}&username={user.username}"
        email = EmailMessage()
        email.subject = "Reset Your Password"
        email.body = "You asked to reset your password, to do so please follow this link : " + url
        email.to = [user.email]
        try:
            email.send()
        except Exception as ex:
            logger.warning(MAIL_ERROR, ex)
            return Response("Error while sending email", status=status.HTTP_400_BAD_REQUEST)
        return Response("Email sent !", status=status.HTTP_200_OK)


class CheckToken(APIView):
    """# Check the token of the user.

    Parameters :
    request (HttpRequest) : the request coming from the front-end

    Return :
    Response (response) : True if the token is correct else False
    """

    @swagger_auto_schema(
        operation_description='Authenticate the token of a user.', responses={200: 'The request went well.'}
    )
    def post(self, request):
        """docstrings."""
        token = request.data['token']
        username = request.data['username']
        user = UserProfile.objects.get(username=username)
        return Response(user.check_password(token))


class CheckPassword(APIView):
    """# Check the password of the user.

    Parameters :
    request (HttpRequest) : the request coming from the front-end

    Return :
    Response (response) : True if the password is correct else False
    """

    @swagger_auto_schema(
        operation_description='Authenticate the token of a user.', responses={200: 'The request went well.'}
    )
    def post(self, request):
        """Check if the pair username password is valid."""
        password = request.data['password']
        username = request.data['username']
        user = authenticate(username=username, password=password)
        return Response(user is not None)


class ResendInscriptionEmail(APIView):
    """Resend the inscription mail to an user."""

    def get(self, request):
        """Resend the inscription mail to an user."""
        try:
            user = UserProfile.objects.get(pk=request.GET.get('userid'))
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.user.has_perm(ADD_USERPROFILE):
            data = {'id': user.pk}
            send_mail_to_setup_password(data)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


def init_database():
    """Initialise the database for tests."""
    # Creation of 3 TeamTypes
    admins = TeamType.objects.create(name="Administrators")
    mms = TeamType.objects.create(name="Maintenance Manager")
    mts = TeamType.objects.create(name="Maintenance Team")

    # Creation of the 3 inital Teams
    Team.objects.create(name="Administrators 1", team_type=admins)
    t_mm1 = Team.objects.create(name="Maintenance Manager 1", team_type=mms)
    t_mt1 = Team.objects.create(name="Maintenance Team 1", team_type=mts)

    # Adding all permissions to admins
    permis = Permission.objects.all()
    for perm in permis:
        admins.perms.add(perm)

    admins._apply_()
    admins.save()
    admins = TeamType.objects.get(name="Administrators")
    t_admin = admins.team_set.all()[0]

    # Adding first user to admins
    user = UserProfile.objects.all()[0]
    user.groups.add(t_admin)
    user.save()

    t_admin.save()
    admins.save()
    mms.save()
    mts.save()

    t_admin.save()
    t_mm1.save()
    t_mt1.save()
