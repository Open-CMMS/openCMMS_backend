from rest_framework.response import Response
from rest_framework.decorators import api_view
from maintenancemanagement.models import Field
from maintenancemanagement.serializers import FieldSerializer

@api_view(['GET'])
def field_list(request):

    if request.method == 'GET':
        field = Field.objects.all()
        serializer = FieldSerializer(field,many=True)
        return Response(serializer.data)
