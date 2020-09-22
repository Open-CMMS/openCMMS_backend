from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from maintenancemanagement.serializers import EquipmentSerializer
from maintenancemanagement.models import Equipment
from django.contrib.auth import authenticate, login, logout

@api_view(['GET', 'POST'])
def equipment_list(request):
    """
        \n# List all equipments or create a new one

        

        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : list all equipments and return the data
        POST request : 
        - create a new equipment, send HTTP 201.  If the request is not valid, send HTTP 400.
        - If the user doesn't have the permissions, it will send HTTP 401.
        - The request must contain name (the name of the equipment (String)) and equipment_type (an id which refers to an equipment type (int))
        - The request can also contain files, a list of id referring to Manual Files (List<int>)
    """

    if request.user.has_perm("maintenancemanagement.view_equipment"):
        if request.method == 'GET':
            equipments = Equipment.objects.all()
            serializer = EquipmentSerializer(equipments, many=True)
            return Response(serializer.data)

    if request.user.has_perm("maintenancemanagement.add_equipment"):
        if request.method == 'POST' :
            serializer = EquipmentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'PUT', 'DELETE'])
def equipment_detail(request, pk):
    """
        \n# Retrieve, update or delete an equipment

        Parameters :
        request (HttpRequest) : the request coming from the front-end
        id (int) : the id of the equipment

        Return :
        response (Response) : the response.

        GET request : return the equipment's data.
        PUT request : change the equipment with the data on the request or if the data isn't well formed, send HTTP 400.
        DELETE request: delete the equipment and send HTTP 204.

        If the user doesn't have the permissions, it will send HTTP 401.
        If the id doesn't exist, it will send HTTP 404.

        The PUT request can contain one or more of the following fields : 
            - name (String): the name of the equipment 
            - equipment_type (int): an id of the updated equipment_type
            - files (List<int>): an id list of the updated list of files

    """
    
    try:
        equipment = Equipment.objects.get(pk=pk)
    except :
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if request.user.has_perm("maintenancemanagement.view_equipment"):
            serializer = EquipmentSerializer(equipment)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'PUT':
        if request.user.has_perm("maintenancemanagement.change_equipment"):
            serializer = EquipmentSerializer(equipment, data = request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'DELETE':
        if request.user.has_perm("maintenancemanagement.delete_equipment"):
            equipment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
