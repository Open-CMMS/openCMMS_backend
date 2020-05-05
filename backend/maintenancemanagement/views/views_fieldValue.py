from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from maintenancemanagement.models import FieldValue, Field
from maintenancemanagement.serializers import FieldValueSerializer

@api_view(['GET'])
def fieldValue_for_field(request, pk):
    """
        Return the fieldValues for a specific field.
    """
    if request.method == 'GET':
        if request.user.has_perm("maintenancemanagement.view_fieldvalue"):
            field = Field.objects.get(id=pk)
            field_values = FieldValue.objects.filter(field=field)
            serializer = FieldValueSerializer(field_values, many=True)
            return Response(serializer.data)
        return Response(status = status.HTTP_401_UNAUTHORIZED)