"""This module defines the views corresponding to teams."""
import logging

from drf_yasg.utils import swagger_auto_schema

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from usersmanagement.models import Team, UserProfile
from usersmanagement.serializers import TeamDetailsSerializer, TeamSerializer

logger = logging.getLogger(__name__)

CHANGE_TEAM = "usersmanagement.change_team"


class TeamList(APIView):
    """Contains HTTP methods GET, POST used on /usermanagement/teams/."""

    @swagger_auto_schema(
        operation_description='Send the list of Team.',
        responses={
            200: 'The request went well.',
            401: 'The client was not authorized to see the ressource.'
        }
    )
    def get(self, request, format='None'):
        """# Implement the GET method.

        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : list all teams and return the data.
        """
        if request.user.has_perm("usersmanagement.view_team"):
            teams = Team.objects.all()
            serializer = TeamSerializer(teams, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Create a new Team.',
        query_serializer=TeamSerializer,
        responses={
            201: 'The Team was created.',
            400: 'The request did not contain valid data.',
            401: 'The user was not authorized to create a Team.'
        }
    )
    def post(self, request, format='None'):
        """Implement the POST method.

        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        POST request :
        - create a new team, send HTTP 201.  If the request is not valid send\
        HTTP 400.
        - If the user doesn't have the permissions, it will send HTTP 401.
        - The request must contain name (the name of the team, string) and\
        team_type (the id of the team_type, int), can contain user_set (the\
        users' id list, []).
        """
        if request.user.has_perm("usersmanagement.add_team"):
            serializer = TeamSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                team = Team.objects.get(pk=serializer.data['id'])
                team.team_type._apply_()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class TeamDetail(APIView):
    """Contains HTTP methods GET, PUT, DELETE used on \
        /usermanagement/teams/{pk}."""

    @swagger_auto_schema(
        operation_description='Send the requested Team.',
        responses={
            200: 'The request went well.',
            401: 'The client was not authorized to see the ressource.',
            404: 'The ressource was not found.'
        }
    )
    def get(self, request, pk, format='None'):
        """Implement the GET method.

        Parameters :
        request (HttpRequest) : the request coming from the front-end
        pk (int) : the id of the team

        Return :
        response (Response) : the response.

        GET request : return the team's data.
        """
        try:
            team = Team.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("usersmanagement.view_team"):
            serializer = TeamDetailsSerializer(team)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Update the ressource.',
        query_serializer=TeamSerializer,
        responses={
            200: 'The request went well.',
            400: 'The request did not contain valid data.',
            401: 'The client was not authorized to update the ressource',
            404: 'The ressource was not found.'
        }
    )
    def put(self, request, pk, format='None'):
        """Implement the PUT method.

        Parameters :
        request (HttpRequest) : the request coming from the front-end
        pk (int) : the id of the team

        Return :
        response (Response) : the response.

        PUT request : Change the team with the data on the request or if the\
        data isn't well formed, send HTTP 400.

        """
        try:
            team = Team.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm(CHANGE_TEAM):
            serializer = TeamSerializer(team, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                team = Team.objects.get(pk=serializer.data['id'])
                team.team_type._apply_()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Delete the Team.',
        responses={
            204: 'The request went well.',
            401: 'The client was not authorized to delete the Team.',
            404: 'The Team was not found.'
        }
    )
    def delete(self, request, pk, format='None'):
        """Implement the DELETE method.

        Parameters :
        request (HttpRequest) : the request coming from the front-end
        pk (int) : the id of the team

        Return :
        response (Response) : the response.

        DELETE request : delete the team and send HTTP 204.
        """
        try:
            team = Team.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("usersmanagement.delete_team"):
            team.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class AddUserToTeam(APIView):
    """# Add and remove users from team.

    Parameters :
    request (HttpRequest) : the request coming from the front-end

    Return :
    response (Response) : the response.

    POST request : add a user to a team and send HTTP 201, must contain\
            id_user (the id of the user to add, int) and id_team (the id of\
                the team where the user will be add, int)
    PUT request : remove a user from a team and send HTTP 201, must\
        contain id_user (the id of the user to remove, int) and\
            id_team (the id of the team where the user will be remove, int)

    If the user doesn't have the permissions, it will send HTTP 401.
    """

    @swagger_auto_schema(
        operation_description='Add the user to the team.',
        responses={
            201: 'The request went well.',
            401: 'The client was not authorized to add a User to a Team.',
        }
    )
    def post(self, request):
        """Implement the POST method.

        ```
        Parameters :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        POST request : add a user to a team and send HTTP 201, must contain
        id_user (the id of the user to add, int) and id_team (the id of the\
        team where the user will be add, int)
        """
        if request.user.has_perm(CHANGE_TEAM):
            user = UserProfile.objects.get(pk=request.data["id_user"])
            team = Team.objects.get(pk=request.data["id_team"])
            team.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Remove the user from the team.',
        responses={
            201: 'The request went well.',
            401: 'The client was not authorized to add a User to a Team.',
        }
    )
    def put(self, request):
        """Add and remove users from team.

        Parameters :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        PUT request : remove a user from a team and send HTTP 201, must\
        contain id_user (the id of the user to remove, int) and id_team (the\
        id of the team where the user will be remove, int)

        If the user doesn't have the permissions, it will send HTTP 401.
        """
        if request.user.has_perm(CHANGE_TEAM):
            user = UserProfile.objects.get(pk=request.data["id_user"])
            team = Team.objects.get(pk=request.data["id_team"])
            team.user_set.remove(user)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


def belongs_to_team(user, team):
    """Check if a user belong to the team.

    Parameters :
    user (UserProfile) : the user to check
    team (Team) : the team to check

    Return :
    boolean : True if the user belongs to team, else False
    """
    return user.groups.filter(id=team.id).exists()
