from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from maintenancemanagement.serializers import TaskTypeSerializer
from maintenancemanagement.models import TaskType
from usersmanagement.models import Team
from django.contrib.auth import authenticate, login, logout

@api_view(['GET', 'POST'])
def taskType_list(request):
    """
        \n# List all taskstypes or create a new one

        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : list all tasktypes and return the data
        POST request : 
        - create a new tasktype, send HTTP 201.  If the request is not valid, send HTTP 400.
        - If the user doesn't have the permissions, it will send HTTP 401.
        - The request must contain name (the name of the tasktype (String))
        
    """
    if request.user.has_perm("maintenancemanagement.view_tasktype"):
        if request.method == 'GET':
            taskTypes = TaskType.objects.all()
            serializer = TaskTypeSerializer(taskTypes, many=True)
            return Response(serializer.data)

    if request.user.has_perm("maintenancemanagement.add_tasktype"):
        if request.method == 'POST' :
            serializer = TaskTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'PUT', 'DELETE'])
def taskType_detail(request, pk):
    """
        \n# Retrieve, update or delete a tasktype

        Parameters :
        request (HttpRequest) : the request coming from the front-end
        id (int) : the id of the tasktype

        Return :
        response (Response) : the response.

        GET request : return the tasktype's data.
        PUT request : change the tasktype with the data on the request or if the data isn't well formed, send HTTP 400.
        DELETE request: delete the tasktype and send HTTP 204.

        If the user doesn't have the permissions, it will send HTTP 401.
        If the id doesn't exist, it will send HTTP 404.

        The PUT request can contain one or more of the following fields : 
            - name (String): The name of the tasktype
    """
    try:
        taskType = TaskType.objects.get(pk=pk)
    except :
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if request.user.has_perm("maintenancemanagement.view_tasktype"):
            serializer = TaskTypeSerializer(taskType)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'PUT':
        if request.user.has_perm("maintenancemanagement.change_tasktype"):
            serializer = TaskTypeSerializer(taskType, data = request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'DELETE':
        if request.user.has_perm("maintenancemanagement.delete_tasktype"):
            taskType.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

