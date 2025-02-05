from django.urls import path
from .views import CustomerRegisterView, CustomerProfileView, ChangePasswordView,PasswordResetConfirmView,PasswordResetRequestView

urlpatterns = [
    path('register/', CustomerRegisterView.as_view(), name='customer-register'),
    path('profile/', CustomerProfileView.as_view(), name='customer-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]