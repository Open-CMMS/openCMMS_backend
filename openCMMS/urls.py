"""openCMMS URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework_swagger.views import get_swagger_view

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

schema_view = get_schema_view(openapi.Info(
    title='OPEN CMMS',
    default_version='v1',
))

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/usersmanagement/', include('usersmanagement.urls')),
    path('api/maintenancemanagement/', include('maintenancemanagement.urls')),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
