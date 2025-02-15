from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
#from django.contrib.auth import authenticate, login, logout
from adminApi.models import Product
from rest_framework.response import Response
from rest_framework import status,generics, pagination
from rest_framework.permissions import IsAuthenticated,BasePermission,AllowAny, IsAuthenticatedOrReadOnly
#from django.contrib.auth.models import User
from .models import Customer,Cart,OrderItem,Review,Order
from .serializers import CustomerSerializer,ProductListSerializer,ProductDetailSerializer,CartSerializer,OrderSerializer,ReviewCreateSerializer,ReviewSerializer
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

'''
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
'''

#Cart 

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    serializer_class = CartSerializer

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
            cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
            if not created:
                cart_item.quantity += int(quantity)
                cart_item.save()
            return Response({"message": "Product added to cart"}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

#place Order
class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        selected_product_ids = request.data.get('product_ids', [])  
        if not selected_product_ids:
            return Response({"error": "No products selected for order"}, status=status.HTTP_400_BAD_REQUEST)
        cart_items = Cart.objects.filter(user=request.user, product__id__in=selected_product_ids)
        if not cart_items.exists():
            return Response({"error": "Selected products not in cart"}, status=status.HTTP_400_BAD_REQUEST)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        order = Order.objects.create(user=request.user, total_price=total_price)
        order_items = [
            OrderItem(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            for cart_item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)
        cart_items.delete()
        subject = "Order Confirmation"
        message = f"Dear {request.user.name},\n\nYour order (ID: {order.id}) has been placed successfully!\nTotal Amount: ${total_price}\n\nThank you for shopping with IntelliWear!"
        recipient_list = [request.user.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        return Response({"message": "Order placed successfully", "order_id": order.id}, status=status.HTTP_201_CREATED)
    
class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    

#Product Detail View With Reviews

class ReviewPagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page'
    max_page_size = 10

class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        """Product details + paginated reviews"""
        product = get_object_or_404(Product, id=product_id)
        product_serializer = ProductDetailSerializer(product)

        reviews = Review.objects.filter(product_id=product_id).order_by('-created_at')
        paginator = ReviewPagination()
        paginated_reviews = paginator.paginate_queryset(reviews, request)
        review_serializer = ReviewSerializer(paginated_reviews, many=True)

        response_data = product_serializer.data
        response_data["reviews"] = review_serializer.data
        return paginator.get_paginated_response(response_data)

    def post(self, request, product_id):
        """New review with multiple images"""
        product = get_object_or_404(Product, id=product_id)
        user = request.user

        if Review.objects.filter(product=product, user=user).exists():
            raise ValidationError("You have already reviewed this product.")

        serializer = ReviewCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, product=product)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)