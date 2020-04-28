from django.urls import path
from maintenancemanagement import views;


urlpatterns = [
]


urlpatterns_equipment = [
    path('equipment/', views.equipment_list, name='equipment-list'),
    path('equipment/<int:pk>', views.equipment_detail, name='equipment-detail'),
]



urlpatterns += urlpatterns_equipment
