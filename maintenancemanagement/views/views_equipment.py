"""This module defines the views corresponding to the equipments."""

from drf_yasg.utils import swagger_auto_schema

from maintenancemanagement.models import Equipment
from maintenancemanagement.serializers import EquipmentSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class EquipmentList(APIView):
    """
    \n# List all equipments or create a new one


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
        if request.user.has_perm("maintenancemanagement.view_equipment"):
            equipments = Equipment.objects.all()
            serializer = EquipmentSerializer(equipments, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Add an Equipment into the database.',
        query_serializer=EquipmentSerializer(many=False),
        responses={
            201: EquipmentSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
        },
    )
    def post(self, request):
        if request.user.has_perm("maintenancemanagement.add_equipment"):
            serializer = EquipmentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class EquipmentDetail(APIView):
    """
        \n# Retrieve, update or delete an equipment

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
            200: EquipmentSerializer(many=False),
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def get(self, request, pk):
        try:
            equipment = Equipment.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.view_equipment"):
            serializer = EquipmentSerializer(equipment)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Update the Equipment corresponding to the given key.',
        query_serializer=EquipmentSerializer(many=False),
        responses={
            200: EquipmentSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def put(self, request, pk):
        try:
            equipment = Equipment.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.change_equipment"):
            serializer = EquipmentSerializer(equipment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

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
        try:
            equipment = Equipment.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.delete_equipment"):
            equipment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
