"""This module defines the views corresponding to the files."""

# Create your views here.
import logging

from drf_yasg.utils import swagger_auto_schema

from django.core.exceptions import ObjectDoesNotExist
from maintenancemanagement.models import File
from maintenancemanagement.serializers import FileSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class FileList(APIView):
    """List all Files or add one."""

    @swagger_auto_schema(
        operation_description='Send the list of File in the database.',
        query_serializer=None,
        responses={
            200: FileSerializer(many=True),
            401: "Unhauthorized",
        },
    )
    def get(self, request):
        """Send the list of File in the database."""
        if request.user.is_authenticated :
            files = File.objects.all()
            serializer = FileSerializer(files, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Add a File into the database.',
        format_data=FileSerializer(many=False),
        responses={
            201: FileSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
        },
    )
    def post(self, request):
        """Add a File into the database."""
        if request.user.is_authenticated :
            serializer = FileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class FileDetail(APIView):
    """Retrieve or delete a File."""

    @swagger_auto_schema(
        operation_description='Send the File corresponding to the given key.',
        query_serializer=None,
        responses={
            200: FileSerializer(many=False),
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def get(self, request, pk):
        """Send the File corresponding to the given key."""
        try:
            file = File.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.is_authenticated :
            serializer = FileSerializer(file)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Delete the File corresponding to the given key.',
        query_serializer=None,
        responses={
            204: "No content",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def delete(self, request, pk):
        """Delete the File corresponding to the given key."""
        try:
            file = File.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.is_authenticated :
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
