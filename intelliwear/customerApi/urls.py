from django.urls import path
from .views import CustomerProfileView,CategoryProductsListView, PlaceOrderViewStripe,ProductDetailView,AddToCartView,OrderListView,GoToCheckoutView, StripeWebhookView, paymentFailView

urlpatterns = [
    #path('register/', CustomerRegisterView.as_view(), name='customer-register'),
    path('', CustomerProfileView.as_view(), name='customer-profile'),
   
    path('api/products/<str:gender>/', CategoryProductsListView.as_view(), name='category-products-list'),
    path('api/product/<uuid:product_id>/', ProductDetailView.as_view(), name='product-detail'),
    path('cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('gocheckout/', GoToCheckoutView.as_view(), name='go-to-checkout'),
    #path("place-order/", PlaceOrderView.as_view(), name="place-order"),
    #path("webhook/", CheckoutWebhookView.as_view(), name="2checkout-webhook"),
    path('orders/', OrderListView.as_view(), name='order-list'), 
    path('place-orderStripe/', PlaceOrderViewStripe.as_view(), name='place-order-stripe'),
    path('stripe-webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    #path('stripe-webhook/', stripe_webhook, name='stripe-webhook'),
    path('payment-success/',OrderListView.as_view()),
    path('payment-failed/',paymentFailView.as_view()),

]