from django.urls import path
from .views import views_equipmentType;
from .views import views_equipment;
from .views import views_task;

from maintenancemanagement.views import views_equipment, views_equipmentType;

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
]

urlpatterns += urlpatterns_equipment
urlpatterns += urlpatterns_equipmenttype
urlpatterns += urlpatterns_task
