"""This module defines the views corresponding to the fields."""

import logging

from drf_yasg.utils import swagger_auto_schema

from maintenancemanagement.models import Field
from maintenancemanagement.serializers import FieldSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class FieldList(APIView):
    r"""
    \n# List all Fields.

    Parameter :
    request (HttpRequest) : the request coming from the front-end

    Return :
    response (Response) : the response.

    GET request : List all Fields
    """

    @swagger_auto_schema(
        operation_description='Send the list of Field in the database.',
        query_serializer=None,
        responses={
            200: FieldSerializer(many=True),
            401: "Unhauthorized",
        },
    )
    def get(self, request):
        """Send the list of Field in the database."""
        if request.user.has_perm("maintenancemanagement.view_field"):
            field = Field.objects.all()
            serializer = FieldSerializer(field, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
