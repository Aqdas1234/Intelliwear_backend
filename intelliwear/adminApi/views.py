from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, generics, status
from .serializers import UserSerializer,ChangePasswordSerializer
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404


from django.contrib.auth.models import User
from customerApi.models import Customer
from customerApi.serializers import CustomerSerializer
#from .models import Product,Size,Color,Media

# Create your views here.
class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


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






class AdminCustomerListView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

class AdminCustomerDetailView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request, username):  # `pk` ki jagah `username` use kiya hai
        customer = get_object_or_404(Customer, user__username=username)  # Look up by username
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def delete(self, request, username):  # Same for delete
        customer = get_object_or_404(Customer, user__username=username)
        customer.user.delete()  
        return Response(status=status.HTTP_204_NO_CONTENT)
