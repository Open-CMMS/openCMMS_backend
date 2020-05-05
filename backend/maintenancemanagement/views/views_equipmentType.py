from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from maintenancemanagement.models import EquipmentType
from maintenancemanagement.serializers import EquipmentTypeSerializer

User = settings.AUTH_USER_MODEL


@api_view(['GET', 'POST'])
def equipmenttype_list(request):
    """
        \n# List all the equipment types or create a new one

        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : list all equipment types and return the data
        POST request : 
        - create a new equipment type, send HTTP 201.  If the request is not valid, send HTTP 400.
        - If the user doesn't have the permissions, it will send HTTP 401.
        - The request must contain name (the name of the equipment type)
    """
    if request.method == 'GET':
        if request.user.has_perm("maintenancemanagement.view_equipmenttype"):
            equipment_types = EquipmentType.objects.all()
            serializer = EquipmentTypeSerializer(equipment_types, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        if request.user.has_perm("maintenancemanagement.add_equipmenttype"):
            serializer = EquipmentTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.erros, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'PUT', 'DELETE'])
def equipmenttype_detail(request, pk):
    """
        \n# Retrieve, update or delete an equipment type

        Parameters :
        request (HttpRequest) : the request coming from the front-end
        id (int) : the id of the equipment type

        Return :
        response (Response) : the response.

        GET request : return the equipment type's data.
        PUT request : change the equipment type with the data on the request or if the data isn't well formed, send HTTP 400.
        DELETE request: delete the equipment type and send HTTP 204.

        If the user doesn't have the permissions, it will send HTTP 401.
        If the id doesn't exist, it will send HTTP 404.

        The PUT request can contain one or more of the following fields : 
            - name : the name of the equipment type


    """

    try:
        equipment_type = EquipmentType.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if request.user.has_perm("maintenancemanagement.view_equipmenttype"):
            serializer = EquipmentTypeSerializer(equipment_type)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'PUT':
        if request.user.has_perm("maintenancemanagement.change_equipmenttype"):
            serializer = EquipmentTypeSerializer(equipment_type, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'DELETE':
        if request.user.has_perm("maintenancemanagement.delete_equipmenttype"):
            equipment_type.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
