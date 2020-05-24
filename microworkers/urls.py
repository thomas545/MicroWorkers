#! URL Configuration

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions, routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="MicroWorkers API",
      default_version='v1',
      description="MicroWorkers Platform",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include('rest_framework.urls')),

    path('', include('users.urls')),
    path('', include('tasks.urls')),

    path('swagger-docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('yasg-docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]



urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
