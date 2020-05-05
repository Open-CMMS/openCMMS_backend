from django.urls import path
from .views import views_equipmentType, views_equipment, views_task, views_taskType, views_fieldValue

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
]

urlpatterns_tasktype = [
    path('tasktypes/', views_taskType.taskType_list, name="tasktype-list"),
    path('tasktypes/<int:pk>/', views_taskType.taskType_detail, name='tasktype-detail')
]

urlpatterns_fieldValue = [
    path('fieldvalues_on_tc/', views_fieldValue.fieldvalues_on_tc, name='fieldvalues-on-tc'),
    path('fieldvalues_on_ec/', views_fieldValue.fieldvalues_on_ec, name='fieldvalues-on-ec'),
    path('fieldvalues_on_all/<int:pk>/', views_fieldValue.fieldvalue_on_all, name='fieldvalues-on-all'),
]

urlpatterns += urlpatterns_equipment
urlpatterns += urlpatterns_equipmenttype
urlpatterns += urlpatterns_task
urlpatterns += urlpatterns_tasktype
urlpatterns += urlpatterns_fieldValue
