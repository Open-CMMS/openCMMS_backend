"""This is our file to provide our endpoints for our utilities."""
from drf_yasg.utils import swagger_auto_schema

from django.core.exceptions import ObjectDoesNotExist
from maintenancemanagement.models import Equipment, FieldObject
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.models import Plugin
from utils.serializers import (
    PluginCreateSerializer,
    PluginDetailsSerializer,
    PluginSerializer,
)


class PluginList(APIView):
    r"""\n# List all plugins or create a new one.

    Parameter :
    request (HttpRequest) : the request coming from the front-end

    Return :
    response (Response) : the response.

    GET request : list all plugins and return the data
    POST request :
    - create a new plugin, send HTTP 201. \
        If the request is not valid, send HTTP 400.
    - If the user doesn't have the permissions, it will send HTTP 401.
    - The request must contain the python file name of the plugin, the targeted
        IP address, the reccurence and the concerned equipment and field.
    """

    @swagger_auto_schema(
        operation_description='Send the list of Plugin in the database.',
        query_serializer=None,
        responses={
            200: PluginSerializer(many=True),
            401: "Unhauthorized",
        },
    )
    def get(self, request):
        """Send the list of Plugin in the database."""
        if request.user.has_perm("utils.view_plugin"):
            plugins = Plugin.objects.all()
            serializer = PluginSerializer(plugins, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Add a Plugin into the database.',
        query_serializer=PluginCreateSerializer(many=False),
        responses={
            201: PluginDetailsSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
        },
    )
    def post(self, request):
        """Add a Plugin into the database."""
        if request.user.has_perm('utils.add_plugin'):
            try:
                FieldObject.objects.get(id=request.data.get("field_object"))
                Equipment.objects.get(id=request.data.get("equipment"))
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            plugin_serializer = PluginCreateSerializer(data=request.data)
            if plugin_serializer.is_valid():
                plugin = plugin_serializer.save()
                plugin_details_serializer = PluginDetailsSerializer(plugin)
                return Response(plugin_details_serializer.data, status=status.HTTP_201_CREATED)
            return Response(plugin_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class PluginDetail(APIView):
    """Retrieve, update or delete an equipment."""

    @swagger_auto_schema(
        operation_description='Send the plugin corresponding to the given key.',
        query_serializer=None,
        reponses={
            200: PluginDetailsSerializer(many=False),
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def get(self, request, pk):
        """Send the plugin corresponding to the given key."""
        try:
            equipment = Plugin.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("utils.view_plugin"):
            serializer = PluginDetailsSerializer(equipment)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Delete the Plugin corresponding to the given key.',
        query_serializer=None,
        responses={
            204: "No content",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def delete(self, request, pk):
        """Delete the Plugin corresponding to the given key."""
        try:
            plugin = Plugin.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("utils.delete_plugin"):
            plugin.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Update the Plugin corresponding to the given key.',
        query_serializer=PluginSerializer(many=False),
        responses={
            200: PluginDetailsSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def put(self, request, pk):
        """Update the Plugin corresponding to the given key."""
        try:
            plugin = Plugin.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("utils.change_plugin"):
            serializer = PluginDetailsSerializer(plugin, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
