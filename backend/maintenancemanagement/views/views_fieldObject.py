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

        GET request : List all fieldObjects and send HTTP 200. If the user doesn't have the permissions, it will send HTTP 401.
        POST request :
        - create a new fieldObject, send HTTP 201.  If the request is not valid, send HTTP 400.
        - If the user doesn't have the permissions, it will send HTTP 401.
        - The request must contain:
            - described_object(String): The described object of this form: "Object: id", example: "Task: 2"
            - field(Int): an id which refers to the concerned field
            - field_value(Int): an id which refers to the concerned field_value
            - value(String): The value to put for the FieldValue
            - description(String): The description of value
    """

    if request.method == 'GET':
        if request.user.has_perm("maintenancemanagement.view_fieldobject"):
            field_objects = FieldObject.objects.all()
            serializer = FieldObjectSerializer(field_objects, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'POST':
        if request.user.has_perm("maintenancemanagement.add_fieldobject"):
            serializer = FieldObjectSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.erros, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET','PUT','DELETE'])
def fieldObject_detail(request,pk):
    """
        Retrieve, update or delete a fieldObject.

        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : Detail the FieldObject, send HTTP 200. If the user doesn't have the permissions, it will send HTTP 401.
        PUT request :
        Update the fieldObject, send HTTP 200. If the request is not valid, send HTTP 400.
        If the user doesn't have the permissions, it will send HTTP 401.
        - The request must contain:
            - described_object(String): The described object of this form: "Object: id", example: "Task: 2"
            - field(Int): an id which refers to the concerned field
            - field_value(Int): an id which refers to the concerned field_value
            - value(String): The value to put for the FieldValue
            - description(String): The description of value

        DELETE request: Delete the fieldObject, send HTTP 204. If the user doesn't have the permissions, it will send HTTP 401.

    """

    try:
        field_object = FieldObject.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method =='GET':
        if request.user.has_perm("maintenancemanagement.view_fieldobject"):
            serializer = FieldObjectSerializer(field_object)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'PUT':
        if request.user.has_perm("maintenancemanagement.change_fieldobject"):
            serializer = FieldObjectSerializer(field_object, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.erros, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'DELETE':
        if request.user.has_perm("maintenancemanagement.delete_fieldobject"):
            field_object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)