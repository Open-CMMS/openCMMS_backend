from django.urls import path
from .views import views_equipmentType;
from .views import views_equipment;

urlpatterns = [
]


urlpatterns_equipment = [
    path('equipment/', views_equipment.equipment_list, name='equipment-list'),
    path('equipment/<int:pk>', views_equipment.equipment_detail, name='equipment-detail'),
]

urlpatterns_equipmenttype = [
    path('equipmenttype/', views_equipmentType.equipmenttype_list, name='equipmenttype-list')
]



urlpatterns += urlpatterns_equipment
urlpatterns += urlpatterns_equipmenttype