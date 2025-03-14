from django.shortcuts import render
#from django.contrib.auth.models import User
from rest_framework import viewsets, status , filters
from customerApi.serializers import UserSerializer
from .serializers import ProductSerializer,CarouselSerializer
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Product,Carousel
from django_filters.rest_framework import DjangoFilterBackend
from .paginations import MyLimitOffsetPagination
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
#from .models import Product,Size,Color,Media
User = get_user_model() 
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.
class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.user_type == 'admin')
    
@extend_schema(tags=["Admin - Profile"])
class ProfileView(APIView):
    permission_classes = [IsSuperUser]

    @extend_schema(
        responses={200: UserSerializer()},
        description="Get the profile details of the logged-in admin."
    )

    def get(self, request):
        serializer = UserSerializer(request.user)  # Directly use User model
        return Response(serializer.data)

    
    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer()},
        description="Update the profile details of the logged-in admin."
    )    

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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


# Admin Customer List View
@extend_schema(tags=["Admin - CustomersListView"])
class AdminCustomerListView(APIView):
    permission_classes = [IsSuperUser]
    pagination_class = MyLimitOffsetPagination 

    @extend_schema(
        parameters=[
            OpenApiParameter(name="limit", description="Number of results per page", required=False, type=int),
            OpenApiParameter(name="offset", description="Pagination offset", required=False, type=int)
        ],
        responses={200: UserSerializer(many=True)}
    )
    def get(self, request):
        users = User.objects.filter(user_type="customer").order_by("-created_at")

        paginator = self.pagination_class()  
        paginated_users = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)

@extend_schema(tags=["Admin - Customers"])
class AdminCustomerDetailView(APIView):
    permission_classes = [IsSuperUser]

    @extend_schema(
        responses={200: UserSerializer},
        description="Retrieve details of a specific customer by user ID.",
    )

    def get(self, request, user_id):  
        user = get_object_or_404(User, id=user_id)  
        serializer = UserSerializer(user) 
        return Response(serializer.data)

    @extend_schema(
        responses={204: OpenApiResponse(description="User deleted successfully")},
        description="Delete a specific customer by user ID.",
    )    

    def delete(self, request, user_id): 
        user = get_object_or_404(User, id=user_id)  
        user.delete() 
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(tags=["Admin - Products"])
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsSuperUser] 
    parser_classes = (MultiPartParser, FormParser)  

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product_type','sizes'] 
    ordering_fields = ['created_at']
    ordering = ['-created_at']  
    pagination_class = MyLimitOffsetPagination 

    @extend_schema(
        responses={200: ProductSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="product_type",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter products by type.",
            )
        ],
        description="Retrieve a list of products with optional filtering by type.",
    )

    def get_queryset(self):
        queryset = Product.objects.all()
        product_type = self.request.query_params.get('product_type')
        size = self.request.query_params.get('size')  
        if product_type:
            queryset = queryset.filter(product_type=product_type)
        if size:
            queryset = queryset.filter(sizes__size=size)  
        return queryset

@extend_schema(tags=["Carousel"])
class CarouselViewSet(viewsets.ModelViewSet):
    queryset = Carousel.objects.all().order_by("-created_at")
    serializer_class = CarouselSerializer
    parser_classes = (MultiPartParser, FormParser) 

    def get_permissions(self):
        if self.action == "list": 
            return [AllowAny()]
        return [IsSuperUser()]  