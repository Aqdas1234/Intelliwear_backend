from .views import RegisterView,LoginView,LogoutView,ChangePasswordView,PasswordResetConfirmView,PasswordResetRequestView
from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title = "Intelliwear Api",
        default_version= 'v1',
        description= "Api Documentation of Intelliwear",
    
    ),
    public=True,
    authentication_classes=[JWTAuthentication],
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', RegisterView.as_view(),name="signup"),
    path('login/', LoginView.as_view(),name="login"),
    path('logout/', LogoutView.as_view(),name="logout"),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('refreshtoken/' , TokenRefreshView.as_view() , name="token_refresh"),


    path('adminApi/', include('adminApi.urls')),
    path('customer/', include('customerApi.urls')),
    path('api-auth/', include('rest_framework.urls')),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
