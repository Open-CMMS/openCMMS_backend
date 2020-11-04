"""This files routes our utilities."""
from django.urls import path
from utils.views import DataProviderDetail, DataProviderList

urlpatterns = []

urlpatterns_dataprovider = [
    path('dataproviders/', DataProviderList.as_view(), name='dataprovider-list'),
    path('dataproviders/<int:pk>/', DataProviderDetail.as_view(), name='dataprovider-detail'),
]

urlpatterns += urlpatterns_dataprovider
