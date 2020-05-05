from rest_framework.response import Response
from rest_framework.decorators import api_view
from maintenancemanagement.models import FieldValue, Field
from maintenancemanagement.serializers import FieldValueSerializer


@api_view(['GET'])
def fieldvalues_on_tc(request):
    field_trigger_conditions = Field.objects.filter(name="Trigger Conditions")[0]
    field_values = FieldValue.objects.filter(field=field_trigger_conditions)
    serializer = FieldValueSerializer(field_values, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def fieldvalues_on_ec(request):
    end_conditions = Field.objects.filter(name="End Conditions")[0]
    print(end_conditions.id)
    field_values = FieldValue.objects.filter(field=end_conditions)
    serializer = FieldValueSerializer(field_values, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def fieldvalue_on_all(request, pk):
    field = Field.objects.get(id=pk)
    field_values = FieldValue.objects.filter(field=field)
    serializer = FieldValueSerializer(field_values, many=True)
    return Response(serializer.data)
