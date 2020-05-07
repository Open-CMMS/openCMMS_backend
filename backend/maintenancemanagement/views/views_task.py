from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from maintenancemanagement.serializers import TaskSerializer
from maintenancemanagement.models import Task, Field, FieldGroup, FieldValue
from usersmanagement.models import Team, UserProfile
from usersmanagement.views.views_team import belongs_to_team
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
        if request.user.has_perm("maintenancemanagement.view_task") or participate_to_task(request.user,task):
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

@api_view(["GET"])
def user_task_list(request, pk):
    """
        \n# List all the tasks the user is assigned to.

        Parameter :
        request (HttpRequest) : the request coming from the front-end
        pk (int) : the user's database id.

        Return :
        response (Response) : the response.

        GET request : list all tasks of the user.
    """
    try:
        user = UserProfile.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.user.has_perm("maintenancemanagement.view_task"):
        #id_team = user.groups.all().values_list("id", flat=True).iterator()
        tasks = Task.objects.filter(teams__pk__in=user.groups.all().values_list("id", flat=True).iterator())
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    else :
        return Response(status=status.HTTP_401_UNAUTHORIZED)

def participate_to_task(user,task):
    """
        \n# Check if a user is assigned to the task

    """
    for team in task.teams.values_list("id", flat=True).iterator():
        belong = belongs_to_team(user,Team.objects.get(id=team))
        if belong:
            return True
    return False


def init_database():
    fieldGr = FieldGroup.objects.create(name="Maintenance", is_equipment=False)

    fieldCriDec = Field.objects.create(name="Trigger Conditions", field_group=fieldGr)
    fieldCriFin = Field.objects.create(name="End Conditions", field_group=fieldGr)

    fieldDateDec = FieldValue.objects.create(value="Date", field=fieldCriDec)
    fieldEntierDec = FieldValue.objects.create(value="Entier", field=fieldCriDec)
    #fieldCaseDec = FieldValue.objects.create(value="Case a cocher", field=fieldCriDec)
    #fieldPhotoDec = FieldValue.objects.create(value="Photo", field=fieldCriDec)
    fieldDecimalDec = FieldValue.objects.create(value="Décimal", field=fieldCriDec)
    fieldDureeDec = FieldValue.objects.create(value="Duree", field=fieldCriDec)

    fieldCaseFin = FieldValue.objects.create(value="Case a cocher", field=fieldCriFin)
    fieldEntierFin = FieldValue.objects.create(value="Valeur numerique à rentrer", field=fieldCriFin)
    fieldStringFin = FieldValue.objects.create(value="Description", field=fieldCriFin)
    fieldPhotoFin =FieldValue.objects.create(value="Photo", field=fieldCriFin)

    fieldGr.save()
    fieldCriDec.save()
    fieldCriFin.save()

    fieldDateDec.save()
    fieldEntierDec.save()
    fieldDecimalDec.save()
    fieldDureeDec.save()

    fieldCaseFin.save()
    fieldEntierFin.save()
    fieldStringFin.save()
    fieldPhotoFin.save()
