"""This is our file to provide our endpoints for our utilities."""
import logging
import os

from drf_yasg.utils import swagger_auto_schema

from django.core.exceptions import ObjectDoesNotExist
from maintenancemanagement.models import Equipment, FieldObject
from openCMMS.settings import BASE_DIR
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.data_provider import (
    DataProviderException,
    add_job,
    scheduler,
    test_dataprovider_configuration,
)
from utils.models import DataProvider
from utils.serializers import (
    DataProviderCreateSerializer,
    DataProviderDetailsSerializer,
    DataProviderRequirementsSerializer,
    DataProviderUpdateSerializer,
)

logger = logging.getLogger(__name__)


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
    - The request must contain the python file name of the dataprovider,\
         the targeted IP address, the reccurence and the concerned \
             equipment and field.
    """

    @swagger_auto_schema(
        operation_description='Send the list of DataProvider in the database.',
        query_serializer=None,
        responses={
            200: DataProviderRequirementsSerializer(many=False),
            401: "Unhauthorized",
        },
    )
    def get(self, request):
        """Send the list of DataProvider in the database."""
        if request.user.has_perm("utils.view_dataprovider"):
            python_files = os.listdir(os.path.join(BASE_DIR, 'utils/data_providers'))
            python_files.pop(python_files.index('__init__.py'))
            if '__pycache__' in python_files:
                python_files.pop(python_files.index('__pycache__'))
            data_providers = DataProvider.objects.all()
            equipments = Equipment.objects.all()
            serializer = DataProviderRequirementsSerializer(
                {
                    'equipments': equipments,
                    'data_providers': data_providers
                }
            )
            dict_res = serializer.data.copy()
            dict_res['python_files'] = python_files
            return Response(dict_res)
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
                logger.info("CREATED DataProvider with {param}".format(param=request.data))
                dataprovider = dataprovider_serializer.save()
                add_job(dataprovider)
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
            logger.info("DELETED DataProvider {dataprovider}".format(dataprovider=repr(dataprovider)))
            if dataprovider.job_id:
                scheduler.remove_job(dataprovider.job_id)
            dataprovider.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Update the DataProvider corresponding to the given key.',
        query_serializer=DataProviderUpdateSerializer(many=False),
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
            serializer = DataProviderUpdateSerializer(dataprovider, data=request.data, partial=True)
            if serializer.is_valid():
                logger.info(
                    "UPDATED DataProvider {dataprovider} with {data}".format(
                        dataprovider=repr(dataprovider), data=request.data
                    )
                )
                dataprovider = serializer.save()
                if dataprovider.is_activated is False:
                    scheduler.pause_job(dataprovider.job_id)
                else:
                    scheduler.resume_job(dataprovider.job_id)
                dataprovider_details_serializer = DataProviderDetailsSerializer(dataprovider)
                return Response(dataprovider_details_serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class TestDataProvider(APIView):
    """This will be our endpoint for testing the config of a dataprovider."""

    @swagger_auto_schema(
        operation_description="Test of data provider's configuration.",
        query_serializer=DataProviderUpdateSerializer(many=False),
        responses={
            200: 'OK',
            400: "Bad request",
            401: "Unhauthorized",
            501: "Not implemented"
        },
    )
    def post(self, request):
        """Test of data provider's configuration."""
        if request.user.has_perm("utils.change_dataprovider") or request.user.has_perm("utils.add_dataprovider"):
            serializer = DataProviderCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            try:
                value = test_dataprovider_configuration(request.data['file_name'], request.data['ip_address'])
                logger.info("TESTED DataProvider with {data}".format(data=request.data))
                return Response(value, status=status.HTTP_200_OK)
            except DataProviderException as e:
                return Response(str(e), status=status.HTTP_501_NOT_IMPLEMENTED)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
