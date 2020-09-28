"""This module defines the views corresponding to the equipment types."""

from drf_yasg.utils import swagger_auto_schema

from django.conf import settings
from maintenancemanagement.models import EquipmentType
from maintenancemanagement.serializers import (
    EquipmentTypeDetailsSerializer,
    EquipmentTypeSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

User = settings.AUTH_USER_MODEL


class EquipmentTypeList(APIView):
    """
        \n# List all the equipment types or create a new one

        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : list all equipment types and return the data
        POST request :
        - create a new equipment type, send HTTP 201.  If the request \
            is not valid, send HTTP 400.
        - If the user doesn't have the permissions, it will send HTTP 401.
        - The request must contain name : the name of the equipment \
            type (String)
        - The request must contain equipment_set : a list (which can \
            be empty) of the equipment id (List<int>)
    """

    @swagger_auto_schema(
        operation_description='Send the list of EquipmentType in the database.',
        query_serializer=None,
        responses={
            200: EquipmentTypeSerializer(many=True),
            401: "Unhauthorized",
        },
    )
    def get(self, request):
        if request.user.has_perm("maintenancemanagement.view_equipmenttype"):
            equipment_types = EquipmentType.objects.all()
            serializer = EquipmentTypeSerializer(equipment_types, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Add an EquipmentType into the database.',
        query_serializer=EquipmentTypeSerializer(many=False),
        responses={
            201: EquipmentTypeSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
        },
    )
    def post(self, request):
        if request.user.has_perm("maintenancemanagement.add_equipmenttype"):
            serializer = EquipmentTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class EquipmentTypeDetail(APIView):
    """
        \n# Retrieve, update or delete an equipment type

        Parameters :
        request (HttpRequest) : the request coming from the front-end
        id (int) : the id of the equipment type

        Return :
        response (Response) : the response.

        GET request : return the equipment type's data.
        PUT request : change the equipment type with the data on the request \
            or if the data isn't well formed, send HTTP 400.
        DELETE request: delete the equipment type and send HTTP 204.

        If the user doesn't have the permissions, it will send HTTP 401.
        If the id doesn't exist, it will send HTTP 404.

        The PUT request can contain one or more of the following fields :
            - name (String): the name of the equipment type
            - equipment_set (List<int>) : a list of equipment's ids


    """

    @swagger_auto_schema(
        operation_description='Send the EquipmentType corresponding to the given key.',
        query_serializer=None,
        responses={
            200: EquipmentTypeDetailsSerializer(many=False),
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def get(self, request, pk):
        try:
            equipment_type = EquipmentType.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.view_equipmenttype"):
            serializer = EquipmentTypeDetailsSerializer(equipment_type)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Update the EquipmentType corresponding to the given key.',
        query_serializer=EquipmentTypeSerializer(many=False),
        responses={
            200: EquipmentTypeSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def put(self, request, pk):
        try:
            equipment_type = EquipmentType.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.change_equipmenttype"):
            serializer = EquipmentTypeSerializer(equipment_type, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Delete the EquipmentType corresponding to the given key.',
        query_serializer=None,
        responses={
            204: "No content",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def delete(self, request, pk):
        try:
            equipment_type = EquipmentType.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.delete_equipmenttype"):
            equipment_type.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
