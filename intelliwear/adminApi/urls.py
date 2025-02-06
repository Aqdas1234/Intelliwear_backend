from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import SellerProfileView,ChangePasswordView,AdminCustomerListView,AdminCustomerDetailView,ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
#router = DefaultRouter()
#router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('seller/profile/', SellerProfileView.as_view(), name='seller-profile-update'),
    path('seller/change-password/', ChangePasswordView.as_view(), name='seller-change-password'),
    path('customers/', AdminCustomerListView.as_view(), name='admin-customer-list'),
    path('customers/<str:username>/', AdminCustomerDetailView.as_view(), name='admin-customer-detail'),
    #path('seller/products/', ProductViewSet.as_view(), name='products'),
    path('', include(router.urls)),

]