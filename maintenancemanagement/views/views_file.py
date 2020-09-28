"""This module defines the views corresponding to the files."""

from drf_yasg.utils import swagger_auto_schema

from maintenancemanagement.models import File
from maintenancemanagement.serializers import FileSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.


class FileList(APIView):
    """
        List all Files or add one. taskType_detailtaskType_detailtaskType_\
            detailtaskType_detailtaskType_detailtaskType_detailtaskType_detailtaskType_detailtaskType_detail
    """

    @swagger_auto_schema(
        operation_description='Send the list of File in the database.',
        query_serializer=None,
        responses={
            200: FileSerializer(many=True),
            401: "Unhauthorized",
        },
    )
    def get(self, request):
        if request.user.has_perm("maintenancemanagement.view_file"):
            files = File.objects.all()
            serializer = FileSerializer(files, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Add a File into the database.',
        query_serializer=FileSerializer(many=False),
        responses={
            201: FileSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
        },
    )
    def post(self, request):
        if request.user.has_perm("maintenancemanagement.add_file"):
            serializer = FileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class FileDetail(APIView):
    """
        Retrieve or delete a File
    """

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
        try:
            file = File.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.view_file"):
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
        try:
            file = File.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.delete_file"):
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
