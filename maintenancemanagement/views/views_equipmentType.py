"""This module defines the views corresponding to the equipment types."""

import logging

from drf_yasg.utils import swagger_auto_schema

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from maintenancemanagement.models import EquipmentType, FieldGroup, Field, FieldValue
from maintenancemanagement.serializers import (
    EquipmentTypeCreateSerializer,
    EquipmentTypeDetailsSerializer,
    EquipmentTypeQuerySerializer,
    EquipmentTypeSerializer,
    EquipmentTypeValidationSerializer,
    FieldCreateSerializer,
    FieldValidationSerializer,
    FieldValueCreateSerializer,
    FieldValueValidationSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)
User = settings.AUTH_USER_MODEL

VIEW_EQUIPMENTTYPE = "maintenancemanagement.view_equipmenttype"
ADD_EQUIPMENTTYPE = "maintenancemanagement.add_equipmenttype"
CHANGE_EQUIPMENTTYPE = "maintenancemanagement.change_equipmenttype"
DELETE_EQUIPMENTTYPE = "maintenancemanagement.delete_equipmenttype"


class EquipmentTypeList(APIView):
    r"""
    \n# List all the equipment types or create a new one.

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
        """Send the list of EquipmentType in the database."""
        if request.user.has_perm(VIEW_EQUIPMENTTYPE):
            equipment_types = EquipmentType.objects.all()
            serializer = EquipmentTypeSerializer(equipment_types, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Add an EquipmentType into the database.',
        query_serializer=EquipmentTypeQuerySerializer(many=False),
        responses={
            201: EquipmentTypeDetailsSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
        },
    )
    def post(self, request):
        """Add an EquipmentType into the database."""
        if request.user.has_perm(ADD_EQUIPMENTTYPE):
            fields = request.data.pop('field', None)
            equipment_type_validation_serializer = EquipmentTypeValidationSerializer(data=request.data)
            if equipment_type_validation_serializer.is_valid():
                data = request.data
                if fields:
                    error = self._validate_fields(fields)
                    if error:
                        return error
                    else:
                        field_group = self._create_fields(request, fields)
                        data.update({'fields_groups': [field_group.id]})
                equipment_type_serializer = EquipmentTypeCreateSerializer(data=data)
                if equipment_type_serializer.is_valid():
                    equipment_type = equipment_type_serializer.save()
                    logger.info(
                        "{user} CREATED EquipmentType with {params}".format(user=request.user, params=request.data)
                    )
                    equipment_type_details = EquipmentTypeDetailsSerializer(equipment_type)
                    return Response(equipment_type_details.data, status=status.HTTP_201_CREATED)
                return Response(equipment_type_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(equipment_type_validation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def _validate_fields(self, fields):
        for field in fields:
            field_values = field.get('value', None)
            field_validation_serializer = FieldValidationSerializer(data=field)
            if not field_validation_serializer.is_valid():
                return Response(field_validation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            if field_values:
                for field_value in field_values:
                    field_value_data = {"value": field_value}
                    field_value_validation_serializer = FieldValueValidationSerializer(data=field_value_data)
                    if not field_value_validation_serializer.is_valid():
                        return Response(field_value_validation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _create_fields(self, request, fields):
        field_group = FieldGroup(name=request.data['name'], is_equipment=True)
        field_group.save()
        for field in fields:
            field_values = field.get('value', None)
            field.update({'field_group': field_group.id})
            field_serializer = FieldCreateSerializer(data=field)
            if field_serializer.is_valid():
                field_instance = field_serializer.save()
                logger.info("{user} CREATED Field with {params}".format(user=request.user, params=field))
                if field_values:
                    for field_value in field_values:
                        field_value_data = {"value": field_value}
                        field_value_data.update({'field': field_instance.id})
                        field_value_serializer = FieldValueCreateSerializer(data=field_value_data)
                        if field_value_serializer.is_valid():
                            field_value_serializer.save()
                            logger.info(
                                "{user} CREATED FieldValue with {params}".format(
                                    user=request.user, params=field_value
                                )
                            )
        return field_group


class EquipmentTypeDetail(APIView):
    r"""
    \n# Retrieve, update or delete an equipment type.

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
        """Send the EquipmentType corresponding to the given key."""
        try:
            equipment_type = EquipmentType.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm(VIEW_EQUIPMENTTYPE):
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
        """Update the EquipmentType corresponding to the given key."""
        try:
            equipment_type = EquipmentType.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm(CHANGE_EQUIPMENTTYPE):
            field_objects = request.data.get("field", None)
            if field_objects is not None :
                self._update_field_values(field_objects)
            serializer = EquipmentTypeSerializer(equipment_type, data=request.data, partial=True)
            if serializer.is_valid():
                logger.info(
                    "{user} UPDATED {object} with {params}".format(
                        user=request.user, object=repr(equipment_type), params=request.data
                    )
                )
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def _update_field_values(self, field_objects):
        for field_object in field_objects:
            field = Field.objects.get(pk=field_object.get('id'))
            new_values = field_object.get('value')
            old_values = field.value_set.all().values_list('value', flat=True)
            for value in new_values:
                if value not in old_values:
                    FieldValue.objects.create(value=value, field=field)

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
        """Delete the EquipmentType corresponding to the given key."""
        try:
            equipment_type = EquipmentType.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm(DELETE_EQUIPMENTTYPE):
            logger.info("{user} DELETED {object}".format(user=request.user, object=repr(equipment_type)))
            equipment_type.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
