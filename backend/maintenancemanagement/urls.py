from django.urls import path
from .views import views_equipmentType
from .views import views_equipment
from .views import views_task
from .views import views_taskType

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
    path('teamtasklist/<int:pk>', views_task.team_task_list, name='team-task-list')
]

urlpatterns_tasktype = [
    path('tasktypes/', views_taskType.taskType_list, name="tasktype-list"),
    path('tasktypes/<int:pk>/', views_taskType.taskType_detail, name='tasktype-detail')
]

urlpatterns += urlpatterns_equipment
urlpatterns += urlpatterns_equipmenttype
urlpatterns += urlpatterns_task
urlpatterns += urlpatterns_tasktype
