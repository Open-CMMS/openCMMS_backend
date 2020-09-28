from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from usersmanagement.models import TeamType
from usersmanagement.serializers import (
    TeamTypeDetailsSerializer,
    TeamTypeSerializer,
)

User = settings.AUTH_USER_MODEL


class TeamTypesList(APIView):
    """# List all the team types or create a new one.

    Parameter :
    request (HttpRequest) : the request coming from the front-end

    Return :
    response (Response) : the response.

    GET request : list all team types and return the data
    POST request :
    - create a new team type, send HTTP 201.  If the request is not valid, send HTTP 400.
    - The request must contain name (the name of the team type, string) and team_set (the id's list of the teams belonging to that type, can be empty, []), can contain perms (the permissions' id list, [])

    If the user doesn't have the permissions, it will send HTTP 401.
    """

    def get(self, request):
        """docstring."""
        if request.user.has_perm("usersmanagement.view_teamtype"):
            group_types = TeamType.objects.all()
            serializer = TeamTypeSerializer(group_types, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        """docstring."""
        if request.user.has_perm("usersmanagement.add_teamtype"):
            serializer = TeamTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
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
    PUT request : change the team type with the data on the request or if the data isn't well formed, send HTTP 400.
    DELETE request: delete the team type and send HTTP 204.

    If the user doesn't have the permissions, it will send HTTP 401.
    If the id doesn't exist, it will send HTTP 404.

    The PUT request can contain one or more of the following fields :
        - name (string) : the name of the team type
        - team_set ([]): the id's list of the teams belonging to that type
        - perms ([]) : the permissions' id list
    """

    def get(self, request, pk):
        """docstring."""
        try:
            group_type = TeamType.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("usersmanagement.view_teamtype"):
            serializer = TeamTypeDetailsSerializer(group_type)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, pk):
        """docstrings."""
        try:
            group_type = TeamType.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("usersmanagement.change_teamtype"):
            serializer = TeamTypeSerializer(group_type, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, pk):
        """docstrings."""
        try:
            group_type = TeamType.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("usersmanagement.delete_teamtype"):
            group_type.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
