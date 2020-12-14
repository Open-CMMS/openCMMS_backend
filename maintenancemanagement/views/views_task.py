"""This module defines the views corresponding to the tasks."""

import logging
from datetime import date

from drf_yasg.utils import swagger_auto_schema

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from maintenancemanagement.models import (
    Field,
    FieldGroup,
    FieldObject,
    File,
    Task,
)
from maintenancemanagement.serializers import (
    FieldObjectCreateSerializer,
    FieldObjectValidationSerializer,
    TaskCreateSerializer,
    TaskDetailsSerializer,
    TaskListingSerializer,
    TaskSerializer,
    TaskTemplateRequirementsSerializer,
    TaskUpdateSerializer,
    TriggerConditionsCreateSerializer,
    TriggerConditionsValidationSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from usersmanagement.models import Team, UserProfile
from usersmanagement.views.views_team import belongs_to_team
from utils.methods import parse_time

logger = logging.getLogger(__name__)
VIEW_TASK = "maintenancemanagement.view_task"
CHANGE_TASK = "maintenancemanagement.change_task"
ADD_TASK = "maintenancemanagement.add_task"
DELETE_TASK = "maintenancemanagement.delete_task"


class TaskList(APIView):
    r"""
    \n# List all tasks or create a new one.

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
            200: TaskListingSerializer(many=True),
            401: "Unhauthorized",
        },
    )
    def get(self, request):
        """Send the list of Task in the database."""
        if request.user.has_perm(VIEW_TASK):
            only_template = request.GET.get("template", None)
            if only_template == "true":
                tasks = Task.objects.filter(is_template=True)
            else:
                tasks = Task.objects.filter(is_template=False)
            serializer = TaskListingSerializer(tasks, many=True)
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
        """Add a Task into the database."""
        if request.user.has_perm(ADD_TASK):
            conditions, task_triggered = self._extract_conditions_from_data(request)
            task_serializer = TaskCreateSerializer(data=request.data)
            if task_serializer.is_valid():
                error = self._validate_conditions(conditions)
                if error:
                    return error
                task = task_serializer.save()
                task.is_triggered = task_triggered
                task.created_by = request.user
                task.save()
                logger.info("{user} CREATED Task with {params}".format(user=request.user, params=request.data))
                self._save_conditions(request, conditions, task)
                return Response(task_serializer.data, status=status.HTTP_201_CREATED)
            return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def _extract_conditions_from_data(self, request):
        trigger_conditions = request.data.pop('trigger_conditions', None)
        end_conditions = request.data.pop('end_conditions', None)
        if not end_conditions:
            check_box = Field.objects.filter(field_group=FieldGroup.objects.get(name="End Conditions")
                                            ).get(name="Checkbox")
            end_conditions = [
                {
                    'field': check_box.id,
                    'value': None,
                    'description': 'Finish task'
                }
            ]  # Add default end_condition
        return (trigger_conditions, end_conditions), trigger_conditions is None

    def _validate_conditions(self, conditions):
        (trigger_conditions, end_conditions) = conditions
        if trigger_conditions:
            for trigger_condition in trigger_conditions:
                validation_serializer = TriggerConditionsValidationSerializer(data=trigger_condition)
                if not validation_serializer.is_valid():
                    return Response(validation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if end_conditions:
            for end_condition in end_conditions:
                validation_serializer = FieldObjectValidationSerializer(data=end_condition)
                if not validation_serializer.is_valid():
                    return Response(validation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _save_conditions(self, request, conditions, task):
        (trigger_conditions, end_conditions) = conditions
        if trigger_conditions:
            for trigger_condition in trigger_conditions:
                trigger_condition.update({'described_object': task})
                condition_serializer = TriggerConditionsCreateSerializer(data=trigger_condition)
                if condition_serializer.is_valid():
                    condition_serializer.save()
                    logger.info(
                        "{user} CREATED FieldObject with {params}".format(user=request.user, params=trigger_condition)
                    )
        if end_conditions:
            for end_condition in end_conditions:
                end_condition.update({'described_object': task})
                condition_serializer = FieldObjectCreateSerializer(data=end_condition)
                if condition_serializer.is_valid():
                    condition_serializer.save()
                    logger.info(
                        "{user} CREATED FieldObject with {params}".format(user=request.user, params=end_condition)
                    )


class TaskDetail(APIView):
    r"""
    \n# Retrieve, update or delete a task.

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
            200: TaskDetailsSerializer(many=False),
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def get(self, request, pk):
        """Send the Task corresponding to the given key."""
        try:
            task = Task.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm(VIEW_TASK) or participate_to_task(request.user, task):
            serializer = TaskDetailsSerializer(task)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description='Update the Task corresponding to the given key.',
        query_serializer=TaskUpdateSerializer(many=False),
        responses={
            200: TaskDetailsSerializer(many=False),
            400: "Bad request",
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def put(self, request, pk):
        """Update the Task corresponding to the given key."""
        if request.user.has_perm(CHANGE_TASK):
            try:
                task = Task.objects.get(pk=pk)
                data = request.data.copy()  # Because request.data is immutable and we will modify its content
                content_type_object = ContentType.objects.get_for_model(task)
                end_conditions = data.pop('end_conditions', None)
                if end_conditions:
                    for end_condition in end_conditions:
                        try:
                            field_object = FieldObject.objects.get(
                                pk=end_condition.get('id'), object_id=task.id, content_type=content_type_object
                            )

                            if end_condition.get('file', None) is not None:
                                end_file = File.objects.get(pk=end_condition.get('file'))
                                task.files.add(end_file)
                                logger.info(
                                    "{user} UPDATED {object} with {params}".format(
                                        user=request.user, object=repr(task), params=data
                                    )
                                )
                                task.save()
                                end_condition.update({'value': end_file.file.path})

                            field_object_serializer = FieldObjectCreateSerializer(
                                field_object, data=end_condition, partial=True
                            )
                            if field_object_serializer.is_valid():
                                logger.info(
                                    "{user} UPDATED {object} with {params}".format(
                                        user=request.user, object=repr(field_object), params=end_condition
                                    )
                                )
                                field_object_serializer.save()

                        except ObjectDoesNotExist:
                            return Response(status=status.HTTP_400_BAD_REQUEST)

                if 'duration' in request.data.keys():
                    data.update({'duration': parse_time(request.data['duration'])})
                serializer = TaskUpdateSerializer(task, data=data, partial=True)
                if serializer.is_valid():
                    logger.info(
                        "{user} UPDATED {object} with {params}".format(
                            user=request.user, object=repr(task), params=data
                        )
                    )
                    task = serializer.save()
                    self._check_if_over(request, task)
                    serializer_details = TaskDetailsSerializer(task)
                    return Response(serializer_details.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def _check_if_over(self, request, task):
        content_type_object = ContentType.objects.get_for_model(task)
        end_fields_objects = FieldObject.objects.filter(
            object_id=task.id, content_type=content_type_object, field__field_group__name='End Conditions'
        )
        over = True
        for end_field_object in end_fields_objects:
            if end_field_object.value is None:
                over = False
        if over is True:
            task.achieved_by = request.user

            content_type_object = ContentType.objects.get_for_model(task)
            if FieldObject.objects.filter(
                object_id=task.id, content_type=content_type_object, field__field_group__name='Trigger Conditions'
            ).count() > 0:
                self._generate_new_task(request, task)
        task.over = over
        logger.info(
            "{user} UPDATED {object} with {params}".format(user=request.user, object=repr(task), params=request.data)
        )
        task.save()

    def _generate_new_task(self, request, task):
        content_type_object = ContentType.objects.get_for_model(task)
        old_trigger_conditions = FieldObject.objects.filter(
            object_id=task.id, content_type=content_type_object, field__field_group__name='Trigger Conditions'
        )
        end_fields_objects = FieldObject.objects.filter(
            object_id=task.id, content_type=content_type_object, field__field_group__name='End Conditions'
        )

        new_task = Task.objects.get(pk=task.pk)
        new_task.pk = None
        new_task.achieved_by = None
        new_task.save()
        for old_trigger_condition in old_trigger_conditions:
            self._create_new_trigger_condition(old_trigger_condition, new_task)
        for end in end_fields_objects:
            FieldObject.objects.create(described_object=new_task, field=end.field, description=end.description)

        logger.info("{user} TRIGGER RECURRENT TASK ON {task}".format(user=request.user, task=new_task))

    def _create_new_trigger_condition(self, trigger_condition, task):
        new_trigger_condition = trigger_condition
        new_trigger_condition.pk = None
        new_trigger_condition.described_object = task
        if trigger_condition.field.name == 'Recurrence':
            new_trigger_condition.save()
            task.end_date = date.today() + parse_time(trigger_condition.value.split('|')[0])
            task.save()
        elif trigger_condition.field.name == 'Frequency':
            splited = trigger_condition.value.split('|')
            trigger_condition.value = '|'.join(splited[:3])
            new_frequency = float(FieldObject.objects.get(id=int(splited[1])).value) + float(splited[0])
            trigger_condition.value += f'|{new_frequency}'
            trigger_condition.save()
        else:
            trigger_condition.save()

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
        """Delete the Task corresponding to the given key."""
        try:
            task = Task.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.has_perm(DELETE_TASK):
            logger.info("{user} DELETED {object}".format(user=request.user, object=repr(task)))
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class AddTeamToTask(APIView):
    r"""
    \n# Assign a team to a task.

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
        """Assign a team to a task."""
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
        """Remove a team from a task."""
        if request.user.has_perm(CHANGE_TASK):
            task = Task.objects.get(pk=request.data["id_task"])
            team = Team.objects.get(pk=request.data["id_team"])
            logger.info(
                "{user} REMOVED {task} FROM {team}".format(user=request.user, task=repr(task), team=repr(team))
            )
            task.teams.remove(team)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class TeamTaskList(APIView):
    r"""
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
        """Send the list of Task corresponding to the given Team key."""
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
    r"""
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
            200: TaskListingSerializer(many=True),
            401: "Unhauthorized",
            404: "Not found",
        },
    )
    def get(self, request, pk):
        """Send the list of Task corresponding to the given User key."""
        try:
            user = UserProfile.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.user.has_perm(VIEW_TASK) or request.user == user:
            tasks = Task.objects.filter(
                teams__pk__in=user.groups.all().values_list("id", flat=True).iterator(), is_template=False
            ).distinct().order_by('over', 'end_date')
            serializer = TaskListingSerializer(tasks, many=True)
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
    r"""\n# Check if a user is assigned to the task."""
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
        """Send the End Conditions and Trigger Conditions. \
            If specified, send the task templates as well."""
        if request.user.has_perm(ADD_TASK):
            serializer = TaskTemplateRequirementsSerializer(1)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
