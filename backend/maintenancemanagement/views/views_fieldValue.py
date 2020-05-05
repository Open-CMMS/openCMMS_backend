from rest_framework.response import Response
from rest_framework.decorators import api_view
from maintenancemanagement.models import FieldValue, Field
from maintenancemanagement.serializers import FieldValueSerializer

@api_view(['GET'])
def fieldvalue_on_specific_field(request, pk):
    field = Field.objects.get(id=pk)
    field_values = FieldValue.objects.filter(field=field)
    serializer = FieldValueSerializer(field_values, many=True)
    return Response(serializer.data)
