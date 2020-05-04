from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from maintenancemanagement.serializers import TaskSerializer
from maintenancemanagement.models import Task
from usersmanagement.models import Team
from django.contrib.auth import authenticate, login, logout

@api_view(['GET', 'POST'])
def task_list(request):
    """
        List all tasks or create a new one
    """
    if request.user.has_perm("maintenancemanagement.view_task"):
        if request.method == 'GET':
            tasks = Task.objects.all()
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data)

    if request.user.has_perm("maintenancemanagement.add_task"):
        if request.method == 'POST' :
            serializer = TaskSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'PUT', 'DELETE'])
def task_detail(request, pk):
    """
        Retrieve, update or delete a task
    """
    try:
        task = Task.objects.get(pk=pk)
    except :
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if request.user.has_perm("maintenancemanagement.view_task"):
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'PUT':
        if request.user.has_perm("maintenancemanagement.change_task"):
            serializer = TaskSerializer(task, data = request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'DELETE':
        if request.user.has_perm("maintenancemanagement.delete_task"):
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST', 'PUT'])
def add_team_to_task(request):
    """
        Assign a team to a task.

        id_task : id of the task to get a team
        id_team : id of the assigned team
    """

    if request.user.has_perm("maintenancemanagement.change_task"):
        if request.method == 'POST':
            task = Task.objects.get(pk=request.data["id_task"])
            team = Team.objects.get(pk=request.data["id_team"])
            task.teams.add(team)
            return Response(status=status.HTTP_201_CREATED)


        elif request.method == 'PUT':
            task = Task.objects.get(pk=request.data["id_task"])
            team = Team.objects.get(pk=request.data["id_team"])
            task.teams.remove(team)
            return Response(status=status.HTTP_201_CREATED)

    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(["GET"])
def team_task_list(request, pk):
    """
    Gives the team's tasks

    Parameters
    ----------
    id_team : id of the wanted team
    """
    try:
        team = Team.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.user.has_perm("maintenancemanagement.view_task"):
        tasks = team.task_set.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    else :
        return Response(status=status.HTTP_401_UNAUTHORIZED)
