"""This module defines the views corresponding to the fields."""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import Field
from ..serializers import FieldSerializer


@api_view(['GET'])
def field_list(request):
    """
        \n# List all Fields.

        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : List all Fields
    """

    if request.method == 'GET':
        if request.user.has_perm("maintenancemanagement.view_field"):
            field = Field.objects.all()
            serializer = FieldSerializer(field, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
