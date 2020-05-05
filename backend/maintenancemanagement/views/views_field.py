from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from maintenancemanagement.models import Field
from maintenancemanagement.serializers import FieldSerializer


@api_view(['GET'])
def field_list(request):
    """
        Get all Field
    """

    if request.method == 'GET':
        if request.user.has_perm("maintenancemanagement.view_field"):
            field = Field.objects.all()
            serializer = FieldSerializer(field,many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

