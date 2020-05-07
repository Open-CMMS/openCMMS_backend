from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from maintenancemanagement.models import FieldObject
from maintenancemanagement.serializers import FieldObjectSerializer
@api_view(['GET','POST'])
def fieldObject_list(request):
    """
        DOC A FAIRE
    """

    if request.method == 'GET':
        field_objects = FieldObject.objects.all()
        serializer = FieldObjectSerializer(field_objects, many=True)
        return Response(serializer.data)