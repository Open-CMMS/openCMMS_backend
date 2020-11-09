"""This files routes our utilities."""
from django.urls import path
from utils.views import DataProviderDetail, DataProviderList, TestDataProvider

urlpatterns = []

urlpatterns_dataprovider = [
    path('dataproviders/', DataProviderList.as_view(), name='dataprovider-list'),
    path('dataproviders/<int:pk>/', DataProviderDetail.as_view(), name='dataprovider-detail'),
    path('dataproviders/test/', TestDataProvider.as_view(), name='dataprovider-test'),
]

urlpatterns += urlpatterns_dataprovider
