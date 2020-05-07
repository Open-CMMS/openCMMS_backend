from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from maintenancemanagement.models import Field
from maintenancemanagement.serializers import FieldSerializer


@api_view(['GET'])
def field_list(request):
    """
        \n# List all Fields

        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : List
        POST request :
        - create a new equipment type, send HTTP 201.  If the request is not valid, send HTTP 400.
        - If the user doesn't have the permissions, it will send HTTP 401.
        - The request must contain name : the name of the equipment type (String)
        - The request must contain equipment_set : a list (which can be empty) of the equipment id (List<int>)
    """

    if request.method == 'GET':
        if request.user.has_perm("maintenancemanagement.view_field"):
            field = Field.objects.all()
            serializer = FieldSerializer(field,many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

