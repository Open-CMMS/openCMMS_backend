"""This module defines the views corresponding to the files."""

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

    def get(self, request):
        if request.user.has_perm("maintenancemanagement.view_file"):
            files = File.objects.all()
            serializer = FileSerializer(files, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

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

    def get(self, request, pk):
        try:
            file = File.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.view_file"):
            serializer = FileSerializer(file)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, pk):
        try:
            file = File.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.delete_file"):
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
