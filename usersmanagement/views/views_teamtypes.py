"""This module defines the views corresponding to team types."""

import logging

from drf_yasg.utils import swagger_auto_schema

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from usersmanagement.models import TeamType
from usersmanagement.serializers import (
    TeamTypeDetailsSerializer,
    TeamTypeSerializer,
)

logger = logging.getLogger(__name__)

User = settings.AUTH_USER_MODEL

VIEW_TEAMTYPE = "usersmanagement.view_teamtype"
ADD_TEAMTYPE = "usersmanagement.add_teamtype"
CHANGE_TEAMTYPE = "usersmanagement.change_teamtype"
DELETE_TEAMTYPE = "usersmanagement.delete_teamtype"


class TeamTypesList(APIView):
    """# List all the team types or create a new one.

    Parameter :
    request (HttpRequest) : the request coming from the front-end

    Return :
    response (Response) : the response.

    GET request : list all team types and return the data
    POST request :
    - create a new team type, send HTTP 201.  If the request is\
         not valid, send HTTP 400.
    - The request must contain name (the name of the team type, string) and \
        team_set (the id's list of the teams belonging to that type, can be \
            empty,[]), can contain perms (the permissions' id list, [])

    If the user doesn't have the permissions, it will send HTTP 401.
    """

    @swagger_auto_schema(
        operation_description='Send the list of all TeamType.',
        responses={
            200: 'The request went well',
            401: 'The client was not authorized to view the ressource.'
        },
    )
    def get(self, request):
        """docstring."""
        if request.user.has_perm(VIEW_TEAMTYPE):
            group_types = TeamType.objects.all()
            serializer = TeamTypeSerializer(group_types, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        query_serializer=TeamTypeSerializer,
        operation_description='Create a new TeamType object and save it in the database.',
        responses={
            201: 'The request went well',
            400: 'The request did not contain valid data.',
            401: 'The client was not authorized to view the ressource.'
        }
    )
    def post(self, request):
        """docstring."""
        if request.user.has_perm(ADD_TEAMTYPE):
            serializer = TeamTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info("{user} CREATED TeamType with {params}".format(user=request.user, params=request.data))
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class TeamTypesDetail(APIView):
    """# Retrieve, update or delete a team type.

    Parameters :
    request (HttpRequest) : the request coming from the front-end
    pk (int) : the id of the team type

    Return :
    response (Response) : the response.

    GET request : return the team type's data.
    PUT request : change the team type with the data on the request or if\
         the data isn't well formed, send HTTP 400.
    DELETE request: delete the team type and send HTTP 204.

    If the user doesn't have the permissions, it will send HTTP 401.
    If the id doesn't exist, it will send HTTP 404.

    The PUT request can contain one or more of the following fields :
        - name (string) : the name of the team type
        - team_set ([]): the id's list of the teams belonging to that type
        - perms ([]) : the permissions' id list
    """

    @swagger_auto_schema(
        operation_description='Send the requested TeamType.',
        responses={
            200: 'The request went well.',
            401: 'The client was not authorized to see the ressource.',
            404: 'The ressource was not found.'
        }
    )
    def get(self, request, pk):
        """docstring."""
        try:
            group_type = TeamType.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm(VIEW_TEAMTYPE):
            serializer = TeamTypeDetailsSerializer(group_type)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Update the ressource.',
        query_serializer=TeamTypeSerializer,
        responses={
            200: 'The request went well.',
            400: 'The request did not contain valid data.',
            401: 'The client was not authorized to update the ressource',
            404: 'The ressource was not found.'
        }
    )
    def put(self, request, pk):
        """docstrings."""
        try:
            group_type = TeamType.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm(CHANGE_TEAMTYPE):
            serializer = TeamTypeSerializer(group_type, data=request.data)
            if serializer.is_valid():
                logger.info(
                    "{user} UPDATED {object} with {params}".format(
                        user=request.user, object=repr(group_type), params=request.data
                    )
                )
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Delete the ressource.',
        responses={
            204: 'The request went well.',
            401: 'The client was not authorized to delete the ressource.',
            404: 'The ressource was not found.'
        }
    )
    def delete(self, request, pk):
        """docstrings."""
        try:
            group_type = TeamType.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm(DELETE_TEAMTYPE):
            logger.info("{user} DELETED {object}".format(user=request.user, object=repr(group_type)))
            group_type.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
