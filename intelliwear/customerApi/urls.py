from django.urls import path
from .views import CustomerProfileView,CategoryProductsListView,ProductDetailView,AddToCartView,PlaceOrderView,OrderListView,CheckoutWebhookView,GoToCheckoutView

urlpatterns = [
    #path('register/', CustomerRegisterView.as_view(), name='customer-register'),
    path('', CustomerProfileView.as_view(), name='customer-profile'),
   
    path('api/products/<str:gender>/', CategoryProductsListView.as_view(), name='category-products-list'),
    path('api/product/<uuid:product_id>/', ProductDetailView.as_view(), name='product-detail'),
    path('cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('gocheckout/', GoToCheckoutView.as_view(), name='go-to-checkout'),
    path("place-order/", PlaceOrderView.as_view(), name="place-order"),
    path("webhook/", CheckoutWebhookView.as_view(), name="2checkout-webhook"),
    path('orders/', OrderListView.as_view(), name='order-list'), 

]