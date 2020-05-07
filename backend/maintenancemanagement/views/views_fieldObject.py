from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from maintenancemanagement.models import FieldObject
from maintenancemanagement.serializers import FieldObjectSerializer


@api_view(['GET','POST'])
def fieldObject_list(request):
    """
        \n# List all fieldObjects or create a new one.

        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : List all fieldObjects
        POST request :
        - create a new fieldObject, send HTTP 201.  If the request is not valid, send HTTP 400.
        - If the user doesn't have the permissions, it will send HTTP 401.
        - The request must contain name : the name of the equipment type (String)
        TODO suite
        - The request must contain equipment_set : a list (which can be empty) of the equipment id (List<int>)
    """

    if request.method == 'GET':
        field_objects = FieldObject.objects.all()
        serializer = FieldObjectSerializer(field_objects, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = FieldObjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.erros, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PUT','DELETE'])
def fieldObject_detail(request,pk):
    """
        Retrieve, update or delete a fieldObject.

        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : Detail the FieldObject
        POST request :
        - create a new fieldObject, send HTTP 201.  If the request is not valid, send HTTP 400.
        - If the user doesn't have the permissions, it will send HTTP 401.
        - The request must contain name : the name of the equipment type (String)
        TODO suite
    """
    try:
        field_object = FieldObject.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method =='GET':
        serializer = FieldObjectSerializer(field_object)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = FieldObjectSerializer(field_object, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.erros, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        field_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)