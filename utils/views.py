"""This is our file to provide our endpoints for our utilities."""
from drf_yasg.utils import swagger_auto_schema

from django.core.exceptions import ObjectDoesNotExist
from maintenancemanagement.models import Equipment, FieldObject
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.data_provider import add_job, scheduler
from utils.models import DataProvider
from utils.serializers import (
    DataProviderCreateSerializer,
    DataProviderDetailsSerializer,
    DataProviderSerializer,
)


class DataProviderList(APIView):
    r"""\n# List all dataproviders or create a new one.

    Parameter :
    request (HttpRequest) : the request coming from the front-end

    Return :
    response (Response) : the response.

    GET request : list all dataproviders and return the data
    POST request :
    - create a new dataprovider, send HTTP 201. \
        If the request is not valid, send HTTP 400.
    - If the user doesn't have the permissions, it will send HTTP 401.
    - The request must contain the python file name of the dataprovider, the targeted
        IP address, the reccurence and the concerned equipment and field.
    """

    @swagger_auto_schema(
        operation_description='Send the list of DataProvider in the database.',
        query_serializer=None,
        responses={
            200: DataProviderSerializer(many=True),
            401: "Unhauthorized",
        },
    )
    def get(self, request):
        """Send the list of DataProvider in the database."""
        if request.user.has_perm("utils.view_dataprovider"):
            dataproviders = DataProvider.objects.all()
            serializer = DataProviderSerializer(dataproviders, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Add a DataProvider into the database.',
        query_serializer=DataProviderCreateSerializer(many=False),
        responses={
            201: DataProviderDetailsSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
        },
    )
    def post(self, request):
        """Add a DataProvider into the database."""
        if request.user.has_perm('utils.add_dataprovider'):
            try:
                FieldObject.objects.get(id=request.data.get("field_object"))
                Equipment.objects.get(id=request.data.get("equipment"))
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            dataprovider_serializer = DataProviderCreateSerializer(data=request.data)
            if dataprovider_serializer.is_valid():
                dataprovider = dataprovider_serializer.save()
                add_job(dataprovider)
                if not dataprovider.is_activated:
                    scheduler.pause_job(dataprovider.job_id)
                dataprovider_details_serializer = DataProviderDetailsSerializer(dataprovider)
                return Response(dataprovider_details_serializer.data, status=status.HTTP_201_CREATED)
            return Response(dataprovider_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class DataProviderDetail(APIView):
    """Retrieve, update or delete an equipment."""

    @swagger_auto_schema(
        operation_description='Send the dataprovider corresponding to the given key.',
        query_serializer=None,
        reponses={
            200: DataProviderDetailsSerializer(many=False),
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def get(self, request, pk):
        """Send the dataprovider corresponding to the given key."""
        try:
            equipment = DataProvider.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("utils.view_dataprovider"):
            serializer = DataProviderDetailsSerializer(equipment)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Delete the DataProvider corresponding to the given key.',
        query_serializer=None,
        responses={
            204: "No content",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def delete(self, request, pk):
        """Delete the DataProvider corresponding to the given key."""
        try:
            dataprovider = DataProvider.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("utils.delete_dataprovider"):
            dataprovider.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Update the DataProvider corresponding to the given key.',
        query_serializer=DataProviderSerializer(many=False),
        responses={
            200: DataProviderDetailsSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def put(self, request, pk):
        """Update the DataProvider corresponding to the given key."""
        try:
            dataprovider = DataProvider.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("utils.change_dataprovider"):
            serializer = DataProviderDetailsSerializer(dataprovider, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                if dataprovider.is_activated:
                    scheduler.resume_job(dataprovider.job_id)
                else:
                    scheduler.pause_job(dataprovider.job_id)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
