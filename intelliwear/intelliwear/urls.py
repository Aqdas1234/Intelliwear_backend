

from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('adminApi/', include('adminApi.urls')),
    path('customerApi/', include('customerApi.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
