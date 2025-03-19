from django.urls import path
from .views import AccessoriesListView, CancelOrderViewStripe, ClothesListView, CreateReviewView, CustomerProfileView,CategoryProductsListView, CustomerReturnRequestView, HomePageProductsView, PlaceOrderViewStripe,ProductDetailView,AddToCartView,OrderListView,GoToCheckoutView, RemoveFromCartView, ShoesListView, StripeWebhookView, UpdateCartView, paymentFailView

urlpatterns = [
    #path('register/', CustomerRegisterView.as_view(), name='customer-register'),
    path('', CustomerProfileView.as_view(), name='customer-profile'),
    path('home/', HomePageProductsView.as_view(), name='homepage-products-list'),
    path('products/<str:gender>/', CategoryProductsListView.as_view(), name='category-products-list'),
    path('product/<uuid:product_id>/', ProductDetailView.as_view(), name='product-detail'),
    path('clothes/', ClothesListView.as_view(), name='clothes-list'),
    path('shoes/', ShoesListView.as_view(), name='shoes-list'),
    path('accessories/', AccessoriesListView.as_view(), name='accessories-list'),
    path('cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('update-cart/', UpdateCartView.as_view(), name='update-cart'),
    path('remove-cart/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('gocheckout/', GoToCheckoutView.as_view(), name='go-to-checkout'),
    #path("place-order/", PlaceOrderView.as_view(), name="place-order"),
    #path("webhook/", CheckoutWebhookView.as_view(), name="2checkout-webhook"),
    path('orders/', OrderListView.as_view(), name='order-list'), 
    path('place-orderStripe/', PlaceOrderViewStripe.as_view(), name='place-order-stripe'),
    path('stripe-webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    #path('stripe-webhook/', stripe_webhook, name='stripe-webhook'),
    path('payment-success/',OrderListView.as_view()),
    path('payment-failed/',paymentFailView.as_view()),
    path('cancel-order/',CancelOrderViewStripe.as_view(),name="cancel-order"),
    path('giveReview/',CreateReviewView.as_view(),name="give-review"),
    path("return-requests/", CustomerReturnRequestView.as_view(), name="customer-return-request"),

]