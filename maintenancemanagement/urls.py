from django.urls import path

from .views import (
    views_equipment,
    views_equipmentType,
    views_field,
    views_fieldObject,
    views_fieldValue,
    views_file,
    views_task,
)

urlpatterns = []

urlpatterns_equipment = [
    path('equipments/', views_equipment.EquipmentList.as_view(), name='equipment-list'),
    path('equipments/<int:pk>/', views_equipment.EquipmentDetail.as_view(), name='equipment-detail'),
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

urlpatterns_fieldValue = [
    path('fieldvalues_for_field/<int:pk>/', views_fieldValue.FieldValueForField.as_view(), name='fieldvalues-on-all'),
]

urlpatterns_field = [
    path('fields/', views_field.FieldList.as_view(), name='field-list'),
]

urlpatterns_file = [
    path('files/', views_file.FileList.as_view(), name='file-list'),
    path('files/<int:pk>/', views_file.FileDetail.as_view(), name='file-detail')
]

urlpatterns_fieldObject = [
    path('fieldobjects/', views_fieldObject.FieldObjectList.as_view(), name='fieldObject-list'),
    path('fieldobjects/<int:pk>/', views_fieldObject.FieldObjectDetail.as_view(), name='fieldObject-detail')
]

urlpatterns += urlpatterns_equipment
urlpatterns += urlpatterns_equipmenttype
urlpatterns += urlpatterns_task
urlpatterns += urlpatterns_fieldValue
urlpatterns += urlpatterns_field
urlpatterns += urlpatterns_file
urlpatterns += urlpatterns_fieldObject
