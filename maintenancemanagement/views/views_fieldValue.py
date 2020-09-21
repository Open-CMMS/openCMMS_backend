from maintenancemanagement.models import Field, FieldValue
from maintenancemanagement.serializers import FieldValueSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def fieldValue_for_field(request, pk):
    """
    \n# List all the fieldValues for a specific field

    Parameter :
    request (HttpRequest) : the request coming from the front-end
    pk (int) : id of the specific field

    Return :
    response (Response) : the response.

    GET request : List all the fieldValues for a specific field
    """
    if request.method == "GET":
        if request.user.has_perm("maintenancemanagement.view_fieldvalue"):
            field = Field.objects.get(id=pk)
            field_values = FieldValue.objects.filter(field=field)
            serializer = FieldValueSerializer(field_values, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
