from django.urls import path
from .views import views_equipmentType, views_equipment, views_task, views_taskType, views_fieldValue, views_field, views_file


urlpatterns = [
]

urlpatterns_equipment = [
    path('equipments/', views_equipment.equipment_list, name='equipment-list'),
    path('equipments/<int:pk>/', views_equipment.equipment_detail, name='equipment-detail'),
]


urlpatterns_equipmenttype = [
    path('equipmenttypes/', views_equipmentType.equipmenttype_list, name='equipmenttype-list'),
    path('equipmenttypes/<int:pk>/', views_equipmentType.equipmenttype_detail, name='equipmenttype-detail'),
]

urlpatterns_task = [
    path('tasks/', views_task.task_list, name='task-list'),
    path('tasks/<int:pk>/', views_task.task_detail, name='task-detail'),
    path('addteamtotask', views_task.add_team_to_task, name='add-team-to-task' ),
    path('teamtasklist/<int:pk>', views_task.team_task_list, name='team-task-list'),
    path('usertasklist/<int:pk>', views_task.user_task_list, name='team-task-list')
]

urlpatterns_tasktype = [
    path('tasktypes/', views_taskType.taskType_list, name="tasktype-list"),
    path('tasktypes/<int:pk>/', views_taskType.taskType_detail, name='tasktype-detail')
]


urlpatterns_fieldValue = [
    path('fieldvalues_for_field/<int:pk>/', views_fieldValue.fieldValue_for_field, name='fieldvalues-on-all'),
]

urlpatterns_field = [
    path('fields/', views_field.field_list, name='field-list'),
]

urlpatterns_file = [
    path('files/', views_file.file_list, name='file-list'),
    path('files/<int:pk>/', views_file.file_detail, name='file-detail')
]

urlpatterns += urlpatterns_equipment
urlpatterns += urlpatterns_equipmenttype
urlpatterns += urlpatterns_task
urlpatterns += urlpatterns_tasktype
urlpatterns += urlpatterns_fieldValue
urlpatterns += urlpatterns_field
urlpatterns += urlpatterns_file
