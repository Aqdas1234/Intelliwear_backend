from django.urls import path
from .views import CustomerProfileView,CategoryProductsListView,ProductDetailView,AddToCartView,PlaceOrderView,OrderListView

urlpatterns = [
    #path('register/', CustomerRegisterView.as_view(), name='customer-register'),
    path('', CustomerProfileView.as_view(), name='customer-profile'),
   
    path('api/products/<str:gender>/', CategoryProductsListView.as_view(), name='category-products-list'),
    path('api/product/<uuid:product_id>/', ProductDetailView.as_view(), name='product-detail'),

    path('cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('place-order/', PlaceOrderView.as_view(), name='place-order'),
    path('orders/', OrderListView.as_view(), name='order-list'), 

]