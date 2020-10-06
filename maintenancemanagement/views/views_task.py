from drf_yasg.utils import swagger_auto_schema

from django.core.exceptions import ObjectDoesNotExist
from maintenancemanagement.models import (
    EquipmentType,
    Field,
    FieldGroup,
    FieldValue,
    Task,
)
from maintenancemanagement.serializers import (
    FieldObjectCreateSerializer,
    FieldObjectValidationSerializer,
    TaskCreateSerializer,
    TaskSerializer,
    TaskTemplateRequirementsSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from usersmanagement.models import Team, UserProfile
from usersmanagement.views.views_team import belongs_to_team

VIEW_TASK = "maintenancemanagement.view_task"
CHANGE_TASK = "maintenancemanagement.change_task"
ADD_TASK = "maintenancemanagement.add_task"


class TaskList(APIView):
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

    @swagger_auto_schema(
        operation_description='Send the list of Task in the database.',
        query_serializer=None,
        responses={
            200: TaskSerializer(many=True),
            401: "Unhauthorized",
        },
    )
    def get(self, request):
        if request.user.has_perm(VIEW_TASK):
            tasks = Task.objects.all()
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Add a Task into the database.',
        query_serializer=TaskCreateSerializer(many=False),
        responses={
            201: TaskCreateSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
        },
    )
    def post(self, request):
        if request.user.has_perm("maintenancemanagement.add_task"):
            conditions = self._extract_conditions_from_data(request)
            task_serializer = TaskCreateSerializer(data=request.data)
            if task_serializer.is_valid():
                for condition in conditions:
                    validation_serializer = FieldObjectValidationSerializer(data=condition)
                    if not validation_serializer.is_valid():
                        return Response(validation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                task = task_serializer.save()
                self._save_conditions(conditions, task)
                return Response(task_serializer.data, status=status.HTTP_201_CREATED)
            return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def _extract_conditions_from_data(self, request):
        trigger_conditions = request.data.pop('trigger_conditions', None)
        end_conditions = request.data.pop('end_conditions', None)
        conditions = []
        if trigger_conditions:
            conditions.extend(trigger_conditions)
        if end_conditions:
            conditions.extend(end_conditions)
        return conditions

    def _save_conditions(self, conditions, task):
        for condition in conditions:
            condition.update({'described_object': task})
            condition_serializer = FieldObjectCreateSerializer(data=condition)
            if condition_serializer.is_valid():
                condition_serializer.save()


class TaskDetail(APIView):
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

    @swagger_auto_schema(
        operation_description='Send the Task corresponding to the given key.',
        query_serializer=None,
        responses={
            200: TaskSerializer(many=False),
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def get(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm(VIEW_TASK) or participate_to_task(request.user, task):
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Update the Task corresponding to the given key.',
        query_serializer=TaskSerializer(many=False),
        responses={
            200: TaskSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def put(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm(CHANGE_TASK):
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Delete the Task corresponding to the given key.',
        query_serializer=None,
        responses={
            204: "No content",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def delete(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm("maintenancemanagement.delete_task"):
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class AddTeamToTask(APIView):
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

    @swagger_auto_schema(
        operation_description='Assign a team to a task.',
        query_serializer=None,
        responses={
            201: "Created",
            401: "Unhauthorized",
        },
    )
    def post(self, request):
        if request.user.has_perm(CHANGE_TASK):
            task = Task.objects.get(pk=request.data["id_task"])
            team = Team.objects.get(pk=request.data["id_team"])
            task.teams.add(team)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Remove a team from a task.',
        query_serializer=None,
        responses={
            201: "Created",
            401: "Unhauthorized",
        },
    )
    def put(self, request):
        if request.user.has_perm(CHANGE_TASK):
            task = Task.objects.get(pk=request.data["id_task"])
            team = Team.objects.get(pk=request.data["id_team"])
            task.teams.remove(team)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class TeamTaskList(APIView):
    """
        \n# List all the tasks a team is assigned to.

        Parameter :
        request (HttpRequest) : the request coming from the front-end
        pk (int) : the team's database id.

        Return :
        response (Response) : the response.

        GET request : list all tasks of a team.
    """

    @swagger_auto_schema(
        operation_description='Send the list of Task corresponding to the given Team key.',
        query_serializer=None,
        responses={
            200: TaskSerializer(many=True),
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def get(self, request, pk):
        try:
            team = Team.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.user.has_perm(VIEW_TASK):
            tasks = team.task_set.all()
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class UserTaskList(APIView):
    """
        \n# List all the tasks the user is assigned to.

        Parameter :
        request (HttpRequest) : the request coming from the front-end
        pk (int) : the user's database id.

        Return :
        response (Response) : the response.

        GET request : list all tasks of the user.
    """

    @swagger_auto_schema(
        operation_description='Send the list of Task corresponding to the given User key.',
        query_serializer=None,
        responses={
            200: TaskSerializer(many=True),
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def get(self, request, pk):
        try:
            user = UserProfile.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.user.has_perm(VIEW_TASK) or request.user == user:
            tasks = Task.objects.filter(teams__pk__in=user.groups.all().values_list("id", flat=True).iterator())
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    operation_description='Check if a user is assigned to the task.',
    query_serializer=None,
    responses={
        200: "Ok",
    },
)
def participate_to_task(user, task):
    """
        \n# Check if a user is assigned to the task

    """
    for team in task.teams.values_list("id", flat=True).iterator():
        belong = belongs_to_team(user, Team.objects.get(id=team))
        if belong:
            return True
    return False


class TaskRequirements(APIView):
    """docstrings."""

    @swagger_auto_schema(
        operation_description='Send the End Conditions and Trigger Conditions. \
            If specified, send the task templates as well.',
    )
    def get(self, request):
        """docstrings."""
        if request.user.has_perm(ADD_TASK):
            serializer = TaskTemplateRequirementsSerializer(1)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    operation_description='Initialize the database with basic groups and fields.',
    query_serializer=None,
    responses={},
)
def init_database():
    field_gr_cri_dec = FieldGroup.objects.create(name="Trigger Conditions", is_equipment=False)

    Field.objects.create(name="Date", field_group=field_gr_cri_dec)
    Field.objects.create(name="Integer", field_group=field_gr_cri_dec)
    Field.objects.create(name="Float", field_group=field_gr_cri_dec)
    Field.objects.create(name="Duration", field_group=field_gr_cri_dec)
    field_recurrence_dec = Field.objects.create(name="Recurrence", field_group=field_gr_cri_dec)

    FieldValue.objects.create(value="Day", field=field_recurrence_dec)
    FieldValue.objects.create(value="Week", field=field_recurrence_dec)
    FieldValue.objects.create(value="Month", field=field_recurrence_dec)
    FieldValue.objects.create(value="Year", field=field_recurrence_dec)

    field_gr_cri_fin = FieldGroup.objects.create(name="End Conditions", is_equipment=False)

    Field.objects.create(name="Checkbox", field_group=field_gr_cri_fin)
    Field.objects.create(name="Integer", field_group=field_gr_cri_fin)
    Field.objects.create(name="Description", field_group=field_gr_cri_fin)
    Field.objects.create(name="Photo", field_group=field_gr_cri_fin)

    field_gr_test = FieldGroup.objects.create(name='FieldGroupTest')
    Field.objects.create(name="FieldWithoutValueTest", field_group=field_gr_test)
    field_with_value = Field.objects.create(name="FieldWithValueTest", field_group=field_gr_test)
    FieldValue.objects.create(value="FieldValueTest", field=field_with_value)
    equip_type = EquipmentType.objects.create(name='EquipmentTypeTest')
    equip_type.fields_groups.add(field_gr_test)
    Task.objects.create(name='TemplateTest', duration='2d', is_template=True, equipment_type=equip_type)
