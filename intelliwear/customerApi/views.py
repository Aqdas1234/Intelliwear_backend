from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from adminApi.models import Product
from rest_framework.response import Response
from rest_framework import status,generics
from rest_framework.permissions import IsAuthenticated,BasePermission
#from django.contrib.auth.models import User
from .models import Customer
from .serializers import CustomerSerializer,ProductListSerializer,ProductDetailSerializer
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'customer') and request.user.customer.user_type == 'customer')
    

class CustomerProfileView(APIView):
    permission_classes = [IsCustomerUser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    serializer_class = CustomerSerializer

    def get(self, request):
        customer = Customer.objects.get(user=request.user)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def put(self, request):
        customer = Customer.objects.get(user=request.user)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        customer = Customer.objects.get(user=request.user)
        customer.user.delete()  # Delete the associated User instance
        return Response(status=status.HTTP_204_NO_CONTENT)
    




class CategoryProductsListView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        gender = self.kwargs['gender'].upper()  
        clothes = Product.objects.filter(product_type='CLOTHES', gender=gender)[:5]
        shoes = Product.objects.filter(product_type='SHOES', gender=gender)[:5]
        accessories = Product.objects.filter(product_type='ACCESSORIES', gender=gender)[:5]
        return list(clothes) + list(shoes) + list(accessories)


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer