from django.urls import path
from utils.views import PluginDetail, PluginList

urlpatterns = []

urlpatterns_plugin = [
    path('plugins/', PluginList.as_view(), name='plugin-list'),
    path('plugins/<int:pk>/', PluginDetail.as_view(), name='plugin-detail'),
]

urlpatterns += urlpatterns_plugin
