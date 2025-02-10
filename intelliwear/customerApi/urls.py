from django.urls import path
from .views import CustomerProfileView,CategoryProductsListView,ProductDetailView

urlpatterns = [
    #path('register/', CustomerRegisterView.as_view(), name='customer-register'),
    path('', CustomerProfileView.as_view(), name='customer-profile'),
   
    path('api/products/<str:gender>/', CategoryProductsListView.as_view(), name='category-products-list'),
    path('api/product/<uuid:pk>/', ProductDetailView.as_view(), name='product-detail'),
]