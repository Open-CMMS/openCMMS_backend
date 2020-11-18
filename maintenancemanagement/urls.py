"""This file contains all maintenance management paths."""

from django.urls import path

from .views import (
    views_equipment,
    views_equipmentType,
    views_field,
    views_file,
    views_task,
)

urlpatterns = []

urlpatterns_equipment = [
    path('equipments/', views_equipment.EquipmentList.as_view(), name='equipment-list'),
    path('equipments/<int:pk>/', views_equipment.EquipmentDetail.as_view(), name='equipment-detail'),
    path('equipments/requirements', views_equipment.EquipmentRequirements.as_view(), name='equipement-requirements'),
]

urlpatterns_equipmenttype = [
    path('equipmenttypes/', views_equipmentType.EquipmentTypeList.as_view(), name='equipmenttype-list'),
    path('equipmenttypes/<int:pk>/', views_equipmentType.EquipmentTypeDetail.as_view(), name='equipmenttype-detail'),
]

urlpatterns_task = [
    path('tasks/', views_task.TaskList.as_view(), name='task-list'),
    path('tasks/<int:pk>/', views_task.TaskDetail.as_view(), name='task-detail'),
    path('addteamtotask', views_task.AddTeamToTask.as_view(), name='add-team-to-task'),
    path('teamtasklist/<int:pk>', views_task.TeamTaskList.as_view(), name='team-task-list'),
    path('usertasklist/<int:pk>', views_task.UserTaskList.as_view(), name='team-task-list'),
    path('tasks/requirements', views_task.TaskRequirements.as_view(), name='task_requirements')
]

urlpatterns_field = [
    path('fields/', views_field.FieldList.as_view(), name='field-list'),
]

urlpatterns_file = [
    path('files/', views_file.FileList.as_view(), name='file-list'),
    path('files/<int:pk>/', views_file.FileDetail.as_view(), name='file-detail')
]

urlpatterns += urlpatterns_equipment
urlpatterns += urlpatterns_equipmenttype
urlpatterns += urlpatterns_task
urlpatterns += urlpatterns_field
urlpatterns += urlpatterns_file
