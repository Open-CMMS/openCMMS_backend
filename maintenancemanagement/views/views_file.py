from maintenancemanagement.models import File
from maintenancemanagement.serializers import FileSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.


@api_view(['GET', 'POST'])
def file_list(request):
    """
        List all Files or add one.
    """

    if request.method == 'GET':
        if request.user.has_perm("maintenancemanagement.view_file"):
            files = File.objects.all()
            serializer = FileSerializer(files, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        if request.user.has_perm("maintenancemanagement.add_file"):
            serializer = FileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'DELETE'])
def file_detail(request, pk):
    """
        Retrieve or delete a File
    """

    try:
        file = File.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if request.user.has_perm("maintenancemanagement.view_file"):
            serializer = FileSerializer(file)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'DELETE':
        if request.user.has_perm("maintenancemanagement.delete_file"):
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
