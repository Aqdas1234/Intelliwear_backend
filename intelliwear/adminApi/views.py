from django.shortcuts import render
#from django.contrib.auth.models import User
from rest_framework import viewsets, generics, status
from .serializers import ProductSerializer,CarouselSerializer
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Product,Carousel

from customerApi.models import Customer
from customerApi.serializers import CustomerSerializer
#from .models import Product,Size,Color,Media

# Create your views here.
class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'customer') and request.user.customer.user_type == 'admin')

class ProfileView(APIView):
    permission_classes = [IsSuperUser]

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
    '''
    def delete(self, request):
        customer = Customer.objects.get(user=request.user)
        customer.user.delete()  # Delete the associated User instance
        return Response(status=status.HTTP_204_NO_CONTENT)
    '''


'''
class SellerProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperUser]

    def get_object(self):
        return self.request.user  



class ChangePasswordView(generics.UpdateAPIView):
    model = User
    permission_classes = [IsSuperUser]
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



'''


class AdminCustomerListView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

class AdminCustomerDetailView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request, user_id):  
        customer = get_object_or_404(Customer, user__id=user_id)  
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def delete(self, request, user_id): 
        customer = get_object_or_404(Customer, user__id=user_id)
        customer.user.delete()  
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSuperUser]  

class CarouselViewSet(viewsets.ModelViewSet):
    queryset = Carousel.objects.all()
    serializer_class = CarouselSerializer
    permission_classes = [IsSuperUser]