from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import RegisterView,LoginView,LogoutView,ChangePasswordView,PasswordResetConfirmView,PasswordResetRequestView , CustomTokenRefreshView
from django.contrib import admin
from django.urls import path,include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', RegisterView.as_view(),name="signup"),
    path('login/', LoginView.as_view(),name="login"),
    path('logout/', LogoutView.as_view(),name="logout"),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('refreshtoken/' , CustomTokenRefreshView.as_view() , name="token_refresh"),


    path('adminApi/', include('adminApi.urls')),
    path('customer/', include('customerApi.urls')),
    path('api-auth/', include('rest_framework.urls')),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),

    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

]

#if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
