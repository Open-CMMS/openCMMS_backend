"""This module defines the views corresponding to the field values."""

from maintenancemanagement.models import Field, FieldValue
from maintenancemanagement.serializers import FieldValueSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class FieldValueForField(APIView):
    """
        \n# List all the fieldValues for a specific field

        Parameter :
        request (HttpRequest) : the request coming from the front-end
        pk (int) : id of the specific field

        Return :
        response (Response) : the response.

        GET request : List all the fieldValues for a specific field
    """

    def get(self, request, pk):
        if request.user.has_perm("maintenancemanagement.view_fieldvalue"):
            field = Field.objects.get(id=pk)
            field_values = FieldValue.objects.filter(field=field)
            serializer = FieldValueSerializer(field_values, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
