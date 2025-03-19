from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ProfileView,AdminCustomerListView,AdminCustomerDetailView,ProductViewSet,CarouselViewSet , AdminOrderListView , AdminUpdateOrderStatusView , AdminAnalyticsView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'carousel', CarouselViewSet,basename='Carousel')


urlpatterns = [
    path('profile/', ProfileView.as_view(), name='seller-profile-update'),
    #path('seller/change-password/', ChangePasswordView.as_view(), name='seller-change-password'),
    path('customers/', AdminCustomerListView.as_view(), name='admin-customer-list'),
    path('orderslist/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('adminanalytics/', AdminAnalyticsView.as_view(), name='admin-analytics-view'),
    path('updateorderstatus/<int:order_id>', AdminUpdateOrderStatusView.as_view(), name='update-order-status'),
    path('customers/<int:user_id>/', AdminCustomerDetailView.as_view(), name='admin-customer-detail'),
    #path('seller/products/', ProductViewSet.as_view(), name='products'),
    path('', include(router.urls)),

]