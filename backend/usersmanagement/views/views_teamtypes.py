from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from usersmanagement.serializers import TeamTypeSerializer
from usersmanagement.models import TeamType
from django.contrib.auth import authenticate, login, logout

User = settings.AUTH_USER_MODEL

@api_view(['GET','POST'])
def teamtypes_list(request):
    """
        List all the team types or add one.
    """

    if request.method == 'GET':
        if request.user.has_perm("usersmanagement.view_teamtype"):
            group_types = TeamType.objects.all()
            serializer = TeamTypeSerializer(group_types, many=True)
            return Response(serializer.data)
        else:
           return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        if request.user.has_perm("usersmanagement.add_teamtype"):
            serializer = TeamTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'PUT', 'DELETE'])
def teamtypes_detail(request,pk):
    """
        Retrieve, update or delete a TeamType
    """

    try:
        group_type = TeamType.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if request.user.has_perm("usersmanagement.view_teamtype"):
            serializer = TeamTypeSerializer(group_type)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'PUT':
        if request.user.has_perm("usersmanagement.change_teamtype"):
            serializer = TeamTypeSerializer(group_type, data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'DELETE':
        if request.user.has_perm("usersmanagement.delete_teamtype"):
            group_type.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
