"""This module defines the views corresponding to the equipments."""

from drf_yasg.utils import swagger_auto_schema

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from maintenancemanagement.models import (
    Equipment,
    EquipmentType,
    Field,
    FieldObject,
)
from maintenancemanagement.serializers import (
    EquipmentCreateSerializer,
    EquipmentDetailsSerializer,
    EquipmentRequirementsSerializer,
    EquipmentSerializer,
    EquipmentUpdateSerializer,
    FieldObjectCreateSerializer,
    FieldObjectNewFieldValidationSerializer,
    FieldObjectUpdateSerializer,
    FieldObjectValidationSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class EquipmentList(APIView):
    r"""\n# List all equipments or create a new one.

    Parameter :
    request (HttpRequest) : the request coming from the front-end

    Return :
    response (Response) : the response.

    GET request : list all equipments and return the data
    POST request :
    - create a new equipment, send HTTP 201. \
        If the request is not valid, send HTTP 400.
    - If the user doesn't have the permissions, it will send HTTP 401.
    - The request must contain the name of the equipment and \
        equipment_type (id which refers to an equipment type)
    - The request can also contain files, a list of id \
        referring to Manual Files (List<int>)
    """

    @swagger_auto_schema(
        operation_description='Send the list of Equipment in the database.',
        query_serializer=None,
        responses={
            200: EquipmentSerializer(many=True),
            401: "Unhauthorized",
        },
    )
    def get(self, request):
        """Send the list of Equipment in the database."""
        if request.user.has_perm("maintenancemanagement.view_equipment"):
            equipments = Equipment.objects.all()
            serializer = EquipmentSerializer(equipments, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Add an Equipment into the database.',
        query_serializer=EquipmentCreateSerializer(many=False),
        responses={
            201: EquipmentSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
        },
    )
    def post(self, request):
        """Add an Equipment into the database."""
        if request.user.has_perm("maintenancemanagement.add_equipment"):
            fields = request.data.pop('field', None)
            equipment_serializer = EquipmentCreateSerializer(data=request.data)
            if equipment_serializer.is_valid():
                error = self._validate_fields(request, fields)
                if error:
                    return error
                else:
                    equipment = equipment_serializer.save()
                    self._save_fields(fields, equipment)
                    equipment_details_serializer = EquipmentDetailsSerializer(equipment)
                    return Response(equipment_details_serializer.data, status=status.HTTP_201_CREATED)
            return Response(equipment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def _get_expected_fields(self, request):
        expected_fields_groups = EquipmentType.objects.get(id=request.data.get('equipment_type')).fields_groups.all()
        expected_fields = []
        if expected_fields_groups:
            for expected_fields_group in expected_fields_groups.all():
                for expected_field in Field.objects.filter(field_group=expected_fields_group):
                    expected_fields.append(expected_field.id)
        return expected_fields

    def _validate_fields(self, request, fields):
        expected_fields = self._get_expected_fields(request)
        if fields:
            for field in fields:
                if field.get('field') in expected_fields:
                    expected_fields.remove(field.get('field'))
                    validation_serializer = FieldObjectValidationSerializer(data=field)
                else:
                    validation_serializer = FieldObjectNewFieldValidationSerializer(data=field)
                if not validation_serializer.is_valid():
                    return Response(validation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if expected_fields:
            return Response(str(expected_fields) + " not expected", status=status.HTTP_400_BAD_REQUEST)

    def _save_fields(self, fields, equipment):
        if fields:
            for field in fields:
                print('le field : ', field)
                if field.get('field', None) is None:
                    field.update({'field': Field.objects.create(name=field.get('name')).pk})
                field.update({'described_object': equipment})
                field_object_serializer = FieldObjectCreateSerializer(data=field)
                if field_object_serializer.is_valid():
                    field_object_serializer.save()


class EquipmentDetail(APIView):
    r"""
    \n# Retrieve, update or delete an equipment.

    Parameters :
    request (HttpRequest) : the request coming from the front-end
    id (int) : the id of the equipment

    Return :
    response (Response) : the response.

    GET request : return the equipment's data.
    PUT request : change the equipment with the data on the request \
            or send HTTP 400 if the data isn't well formed.
    DELETE request: delete the equipment and send HTTP 204.

    If the user doesn't have the permissions, it will send HTTP 401.
    If the id doesn't exist, it will send HTTP 404.

    The PUT request can contain one or more of the following fields :
        - name (String): the name of the equipment
        - equipment_type (int): an id of the updated equipment_type
        - files (List<int>): an id list of the updated list of files
    """

    @swagger_auto_schema(
        operation_description='Send the Equipment corresponding to the given key.',
        query_serializer=None,
        responses={
            200: EquipmentDetailsSerializer(many=False),
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def get(self, request, pk):
        """Send the Equipment corresponding to the given key."""
        try:
            equipment = Equipment.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.view_equipment"):
            serializer = EquipmentDetailsSerializer(equipment)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Update the Equipment corresponding to the given key.',
        query_serializer=EquipmentUpdateSerializer(many=False),
        responses={
            200: EquipmentDetailsSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def put(self, request, pk):
        """Update the Equipment corresponding to the given key."""
        try:
            equipment = Equipment.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.change_equipment"):
            print("La requete : ", request.data)
            field_objects = request.data.pop('field', None)
            equipment_serializer = EquipmentUpdateSerializer(equipment, data=request.data, partial=True)
            if equipment_serializer.is_valid():
                if request.data.get('equipment_type', None) is not None:
                    if equipment.equipment_type.pk == request.data.get('equipment_type'):
                        error = self._validate_modification_fields(request, field_objects)
                        if error:
                            return error
                        else:
                            equipment = equipment_serializer.save()
                            self._save_modification_fields(field_objects, equipment)
                            equipment_details_serializer = EquipmentDetailsSerializer(equipment)
                            return Response(equipment_details_serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        error = self._validate_fields(request, field_objects)
                        if error:
                            return error
                        else:
                            content_type = ContentType.objects.get_for_model(equipment)
                            FieldObject.objects.filter(object_id=equipment.pk, content_type=content_type).delete()
                            equipment = equipment_serializer.save()
                            self._save_fields(field_objects, equipment)
                            equipment_details_serializer = EquipmentDetailsSerializer(equipment)
                            return Response(equipment_details_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    equipment_serializer.save()
                    return Response(equipment_serializer.data, status=status.HTTP_200_OK)
            return Response(equipment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def _get_expected_fields(self, request):
        expected_fields_groups = EquipmentType.objects.get(id=request.data.get('equipment_type')).fields_groups.all()
        expected_fields = []
        if expected_fields_groups:
            for expected_fields_group in expected_fields_groups.all():
                for expected_field in Field.objects.filter(field_group=expected_fields_group):
                    expected_fields.append(expected_field.id)
        return expected_fields

    def _validate_fields(self, request, fields):
        expected_fields = self._get_expected_fields(request)
        if fields:
            for field in fields:
                if field.get('field') in expected_fields:
                    expected_fields.remove(field.get('field'))
                    validation_serializer = FieldObjectValidationSerializer(data=field)
                else:
                    validation_serializer = FieldObjectNewFieldValidationSerializer(data=field)
                if not validation_serializer.is_valid():
                    return Response(validation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if expected_fields:
            return Response(str(expected_fields) + " not expected", status=status.HTTP_400_BAD_REQUEST)

    def _save_fields(self, fields, equipment):
        if fields:
            for field in fields:
                print('le field : ', field)
                if field.get('field', None) is None:
                    field.update({'field': Field.objects.create(name=field.get('name')).pk})
                field.update({'described_object': equipment})
                field_object_serializer = FieldObjectCreateSerializer(data=field)
                if field_object_serializer.is_valid():
                    field_object_serializer.save()

    def _validate_modification_fields(self, request, field_objects):
        if field_objects:
            for field_object in field_objects:
                field = Field.objects.get(pk=field_object.get('field'))
                if field.value_set is not None and field_object.get('field_value', None) is not None:
                    if field_object.get('field_value').get('value', None) not in field.value_set.values_list(
                        'value', flat=True
                    ):
                        return Response(
                            field_object.get('field_value', None).get('value', None),
                            " is not a valid value",
                            status=status.HTTP_400_BAD_REQUEST
                        )
                elif field_object.get('value', None) is None:
                    return Response(field_object.get('name') + " cant be null !", status=status.HTTP_400_BAD_REQUEST)

    def _save_modification_fields(self, field_objects, equipment):
        if field_objects:
            for field_object_data in field_objects:
                field_object = FieldObject.objects.get(pk=field_object_data.get('id'))
                if field_object_data.get('field_value') is not None:
                    field_object_data.update({"value": field_object_data.get('field_value').get('value')})

                field_object_serializer = FieldObjectUpdateSerializer(
                    field_object, data=field_object_data, partial=True
                )
                if field_object_serializer.is_valid():
                    field_object_serializer.save()
                print(
                    "le field object concerné après la save : ", str(field_object.id), ' : ', field_object.value,
                    " and ", field_object.field_value
                )

    @swagger_auto_schema(
        operation_description='Delete the Equipment corresponding to the given key.',
        query_serializer=None,
        responses={
            204: "No content",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def delete(self, request, pk):
        """Delete the Equipment corresponding to the given key."""
        try:
            equipment = Equipment.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.delete_equipment"):
            equipment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class EquipmentRequirements(APIView):
    """The view to get all equipements with their values."""

    @swagger_auto_schema(
        operation_description='Send the list of equipement types with their fields and the values associated.',
        responses={200: 'The request went well.'}
    )
    def get(self, request):
        """Send the list of equipement types with their fields \
            and the values associated."""
        if request.user.has_perm("maintenancemanagement.add_equipment"):
            equipment_types = EquipmentType.objects.all()
            serializer = EquipmentRequirementsSerializer(equipment_types, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
