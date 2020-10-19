"""This module defines the views corresponding to the field objects."""

from drf_yasg.utils import swagger_auto_schema

from django.core.exceptions import ObjectDoesNotExist
from maintenancemanagement.models import FieldObject
from maintenancemanagement.serializers import FieldObjectSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class FieldObjectList(APIView):
    r"""
    \n# List all fieldObjects or create a new one.

    Parameter :
    request (HttpRequest) : the request coming from the front-end

    Return :
    response (Response) : the response.

    GET request : List all fieldObjects and send HTTP 200. If the user \
        doesn't have the permissions, it will send HTTP 401.
    POST request :
    - create a new fieldObject, send HTTP 201.  If the request is not \
        valid, send HTTP 400.
    - If the user doesn't have the permissions, it will send HTTP 401.
    - The request must contain:
        - described_object(String): The described object of this form: \
            "Object: id", example: "Task: 2"
        - field(Int): an id which refers to the concerned field
        - field_value(Int): an id which refers to the concerned field_value
        - value(String): The value to put for the FieldValue
        - description(String): The description of value
    """

    @swagger_auto_schema(
        operation_description='Send the list of FieldObject in the database.',
        query_serializer=None,
        responses={
            200: FieldObjectSerializer(many=True),
            401: "Unhauthorized",
        },
    )
    def get(self, request):
        """Send the list of FieldObject in the database."""
        if request.user.has_perm("maintenancemanagement.view_fieldobject"):
            field_objects = FieldObject.objects.all()
            serializer = FieldObjectSerializer(field_objects, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Add a FieldObject into the database.',
        query_serializer=FieldObjectSerializer(many=False),
        responses={
            201: FieldObjectSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
        },
    )
    def post(self, request):
        """Add a FieldObject into the database."""
        if request.user.has_perm("maintenancemanagement.add_fieldobject"):
            serializer = FieldObjectSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class FieldObjectDetail(APIView):
    r"""
    Retrieve, update or delete a fieldObject.

    Parameter :
    request (HttpRequest) : the request coming from the front-end

    Return :
    response (Response) : the response.

    GET request : Detail the FieldObject, send HTTP 200. If the user \
        doesn't have the permissions, it will send HTTP 401.
    PUT request :
    Update the fieldObject, send HTTP 200. If the request is not \
        valid, send HTTP 400.
    If the user doesn't have the permissions, it will send HTTP 401.
    - The request must contain:
        - described_object(String): The described object of this \
            form: "Object: id", example: "Task: 2"
        - field(Int): an id which refers to the concerned field
        - field_value(Int): an id which refers to the concerned field_value
        - value(String): The value to put for the FieldValue
        - description(String): The description of value

    DELETE request: Delete the fieldObject, send HTTP 204. If the user \
        doesn't have the permissions, it will send HTTP 401.
    """

    @swagger_auto_schema(
        operation_description='Send the FieldObject corresponding to the given key.',
        query_serializer=None,
        responses={
            200: FieldObjectSerializer(many=False),
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def get(self, request, pk):
        """Send the FieldObject corresponding to the given key."""
        try:
            field_object = FieldObject.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.view_fieldobject"):
            serializer = FieldObjectSerializer(field_object)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Update the FieldObject corresponding to the given key.',
        query_serializer=FieldObjectSerializer(many=False),
        responses={
            200: FieldObjectSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def put(self, request, pk):
        """Update the FieldObject corresponding to the given key."""
        try:
            field_object = FieldObject.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.change_fieldobject"):
            serializer = FieldObjectSerializer(field_object, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Delete the FieldObject corresponding to the given key.',
        query_serializer=None,
        responses={
            204: "No content",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def delete(self, request, pk):
        """Delete the FieldObject corresponding to the given key."""
        try:
            field_object = FieldObject.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.delete_fieldobject"):
            field_object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
