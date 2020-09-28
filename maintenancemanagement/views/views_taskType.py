"""This module defines the views corresponding to the task types."""

from drf_yasg.utils import swagger_auto_schema

from maintenancemanagement.models import TaskType
from maintenancemanagement.serializers import TaskTypeSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class TaskTypeList(APIView):
    """
        \n# List all taskstypes or create a new one

        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : list all tasktypes and return the data
        POST request :
        - create a new tasktype, send HTTP 201.  If the request \
            is not valid, send HTTP 400.
        - If the user doesn't have the permissions, it will send HTTP 401.
        - The request must contain name (the name of the tasktype (String))

    """

    @swagger_auto_schema(
        operation_description='Send the list of TaskType in the database.',
        query_serializer=None,
        responses={
            200: TaskTypeSerializer(many=True),
            401: "Unhauthorized",
        },
    )
    def get(self, request):
        if request.user.has_perm("maintenancemanagement.view_tasktype"):
            task_types = TaskType.objects.all()
            serializer = TaskTypeSerializer(task_types, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Add a TaskType into the database.',
        query_serializer=TaskTypeSerializer(many=False),
        responses={
            201: TaskTypeSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
        },
    )
    def post(self, request):
        if request.user.has_perm("maintenancemanagement.add_tasktype"):
            serializer = TaskTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class TaskTypeDetail(APIView):
    """
        \n# Retrieve, update or delete a tasktype

        Parameters :
        request (HttpRequest) : the request coming from the front-end
        id (int) : the id of the tasktype

        Return :
        response (Response) : the response.

        GET request : return the tasktype's data.
        PUT request : change the tasktype with the data on the request\
             or if the data isn't well formed, send HTTP 400.
        DELETE request: delete the tasktype and send HTTP 204.

        If the user doesn't have the permissions, it will send HTTP 401.
        If the id doesn't exist, it will send HTTP 404.

        The PUT request can contain one or more of the following fields :
            - name (String): The name of the tasktype
    """

    @swagger_auto_schema(
        operation_description='Send the TaskType corresponding to the given key.',
        query_serializer=None,
        responses={
            200: TaskTypeSerializer(many=False),
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def get(self, request, pk):
        try:
            task_type = TaskType.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.view_tasktype"):
            serializer = TaskTypeSerializer(task_type)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Update the TaskType corresponding to the given key.',
        query_serializer=TaskTypeSerializer(many=False),
        responses={
            200: TaskTypeSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def put(self, request, pk):
        try:
            task_type = TaskType.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.change_tasktype"):
            serializer = TaskTypeSerializer(task_type, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Delete the TaskType corresponding to the given key.',
        query_serializer=None,
        responses={
            204: "No content",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def delete(self, request, pk):
        try:
            task_type = TaskType.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.delete_tasktype"):
            task_type.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
