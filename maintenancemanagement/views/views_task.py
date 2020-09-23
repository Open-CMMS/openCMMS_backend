from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ...usersmanagement.models import Team, UserProfile
from ...usersmanagement.views.views_team import belongs_to_team
from ..models import Field, FieldGroup, FieldValue, Task
from ..serializers import TaskSerializer

VIEW_TASK = "maintenancemanagement.view_task"


@api_view(['GET', 'POST'])
def task_list(request):
    """
        \n# List all tasks or create a new one



        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : list all tasks and return the data
        POST request :
        - create a new task, send HTTP 201.  If the request is not valid,\
             send HTTP 400.
        - If the user doesn't have the permissions, it will send HTTP 401.
        - The request must contain name (the name of the task (String)) and \
            description (a description of the task (String))
        - The request can also contain :
            - end_date (String): Date (format DD-MM-YYYY) of the deadline
            - time (String): estimated duration of the task
            - is_template (Boolean): boolean to specify if this task is \
                just a template or not
            - equipment (int): an id which refers to the concerned equipment
            - teams (List<int>): an id list of the teams in charge of this task
            - task_type (int): an id which refers to the task_type of this task
            - files (List<int>): an id list of the files explaining this task
    """

    if request.user.has_perm(VIEW_TASK) and request.method == 'GET':
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    if request.user.has_perm("maintenancemanagement.add_task") and request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'PUT', 'DELETE'])
def task_detail(request, pk):
    """
        \n# Retrieve, update or delete a task

        Parameters :
        request (HttpRequest) : the request coming from the front-end
        id (int) : the id of the task

        Return :
        response (Response) : the response.

        GET request : return the task's data.
        PUT request : change the task with the data on the request \
            or if the data isn't well formed, send HTTP 400.
        DELETE request: delete the task and send HTTP 204.

        If the user doesn't have the permissions, it will send HTTP 401.
        If the id doesn't exist, it will send HTTP 404.

        The PUT request can contain one or more of the following fields :
            - name (String): The name of the task
            - description (String): The description of the task
            - end_date (String): Date (format DD-MM-YYYY) of the deadline
            - time (String): estimated duration of the task
            - is_template (Boolean): boolean to specify if this task is just \
                a template or not
            - equipment (int): an id which refers to the concerned equipment
            - teams (List<int>): an id list of the teams in charge of this task
            - task_type (int): an id which refers to the task_type of this task
            - files (List<int>): an id list of the files explaining this task


    """

    try:
        task = Task.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if request.user.has_perm(VIEW_TASK) or participate_to_task(request.user, task):
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'PUT':
        if request.user.has_perm("maintenancemanagement.change_task"):
            serializer = TaskSerializer(task, data=request.data, partial=True)
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
        \n# Assign a team to a task

        Parameters :
        request (HttpRequest) : the request coming from the front-end
        id (int) : the id of the task

        Return :
        response (Response) : the response.

        POST request : add team to task
        PUT request : remove team from task

        If the user doesn't have the permissions, it will send HTTP 401.

        Both request must contain :
            - id_task : the id of the task we want to edit
            - id_team : the id ot the team we want to add/remove \
                to/from the task


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
        \n# List all the tasks a team is assigned to.

        Parameter :
        request (HttpRequest) : the request coming from the front-end
        pk (int) : the team's database id.

        Return :
        response (Response) : the response.

        GET request : list all tasks of a team.
    """
    try:
        team = Team.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.user.has_perm(VIEW_TASK):
        tasks = team.task_set.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    else:
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

    if request.user.has_perm(VIEW_TASK) or request.user == user:
        tasks = Task.objects.filter(teams__pk__in=user.groups.all().values_list("id", flat=True).iterator())
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


def participate_to_task(user, task):
    """
        \n# Check if a user is assigned to the task

    """
    for team in task.teams.values_list("id", flat=True).iterator():
        belong = belongs_to_team(user, Team.objects.get(id=team))
        if belong:
            return True
    return False


def init_database():
    field_gr = FieldGroup.objects.create(name="Maintenance", is_equipment=False)

    field_cri_dec = Field.objects.create(name="Trigger Conditions", field_group=field_gr)
    field_cri_fin = Field.objects.create(name="End Conditions", field_group=field_gr)

    field_date_dec = FieldValue.objects.create(value="Date", field=field_cri_dec)
    field_entier_dec = FieldValue.objects.create(value="Entier", field=field_cri_dec)
    field_decimal_dec = FieldValue.objects.create(value="Décimal", field=field_cri_dec)
    field_duree_dec = FieldValue.objects.create(value="Duree", field=field_cri_dec)

    field_case_fin = FieldValue.objects.create(value="Case a cocher", field=field_cri_fin)
    field_entier_fin = FieldValue.objects.create(value="Valeur numerique à rentrer", field=field_cri_fin)
    field_string_fin = FieldValue.objects.create(value="Description", field=field_cri_fin)
    field_photo_fin = FieldValue.objects.create(value="Photo", field=field_cri_fin)

    field_gr.save()
    field_cri_dec.save()
    field_cri_fin.save()

    field_date_dec.save()
    field_entier_dec.save()
    field_decimal_dec.save()
    field_duree_dec.save()

    field_case_fin.save()
    field_entier_fin.save()
    field_string_fin.save()
    field_photo_fin.save()
