from itertools import chain
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
#from django.forms import ValidationError
import uuid
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
#from django.core.mail import send_mail
from django.conf import settings
from adminApi.models import Product
from rest_framework.response import Response
from rest_framework import status,generics, pagination,filters
from rest_framework.permissions import IsAuthenticated,BasePermission,AllowAny
from .models import Cart,OrderItem,Review,Order,Payment,ShippingAddress
from .serializers import ProductListSerializer,ProductDetailSerializer,OrderSerializer,ReviewSerializer, UserSerializer
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination


class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.user_type == 'customer')
    
class CustomerProfileView(APIView):
    permission_classes = [IsCustomerUser]  # Ensure correct permission
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    @extend_schema(
        responses={200: UserSerializer},
        description="Get the profile details of the logged-in user."
    )

    def get(self, request):
        serializer = UserSerializer(request.user)  # Directly use User model
        return Response(serializer.data)

    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer},
        description="Update the profile details of the logged-in user."
    )      

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: OpenApiResponse(description="No Content")},
        description="Delete the user account."
    )   

    def delete(self, request):
        request.user.delete()  # Delete the user account
        return Response(status=status.HTTP_204_NO_CONTENT)


class HomePageProductsView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: ProductListSerializer(many=True)},
        description="Retrieve the latest products from each category for the homepage."
    )
    def get_queryset(self):
        clothes = Product.objects.filter(product_type='CLOTHES').order_by('-created_at')[:8]
        shoes = Product.objects.filter(product_type='SHOES').order_by('-created_at')[:8]
        accessories = Product.objects.filter(product_type='ACCESSORIES').order_by('-created_at')[:8]
        return chain(clothes,shoes,accessories)
    

class CategoryProductsListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer

    @extend_schema(
        responses={200: ProductListSerializer(many=True)},
        description="Retrieve category-specific products based on gender."
    )
    def get_queryset(self):
        gender = self.kwargs['gender'].upper()  
        clothes = Product.objects.filter(product_type='CLOTHES', gender=gender)[:8]
        shoes = Product.objects.filter(product_type='SHOES', gender=gender)[:8]
        accessories = Product.objects.filter(product_type='ACCESSORIES', gender=gender)[:8]
        return chain(clothes,shoes,accessories)


class CustomPagination(PageNumberPagination):
    page_size = 32  
    page_size_query_param = 'page_size'  
    max_page_size = 100  


class ClothesListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'colors', 'sizes'] 
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

    @extend_schema(
        responses={200: ProductListSerializer(many=True)},
        description="Retrieve a paginated list of clothes products with filtering options."
    )
    def get_queryset(self):
        queryset = Product.objects.filter(product_type='CLOTHES').order_by('-created_at')
        gender = self.request.query_params.get('gender', None)
        if gender:
            queryset = queryset.filter(gender=gender.upper())
        return queryset

class ShoesListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'colors', 'sizes'] 
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

    @extend_schema(
        responses={200: ProductListSerializer(many=True)},
        description="Retrieve a paginated list of shoe products with filtering options."
    )
    def get_queryset(self):
        queryset = Product.objects.filter(product_type='SHOES').order_by('-created_at')
        gender = self.request.query_params.get('gender', None)
        if gender:
            queryset = queryset.filter(gender=gender.upper())
        return queryset


class AccessoriesListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'colors', 'sizes'] 
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

    @extend_schema(
        responses={200: ProductListSerializer(many=True)},
        description="Retrieve a paginated list of accessories products with filtering options."
    )
    def get_queryset(self):
        queryset = Product.objects.filter(product_type='ACCESSORIES').order_by('-created_at')
        gender = self.request.query_params.get('gender', None)
        if gender:
            queryset = queryset.filter(gender=gender.upper())
        return queryset



'''
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
'''

#Cart 

class AddToCartView(APIView):
    permission_classes = [IsCustomerUser]  
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response({"error": "Quantity must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid quantity format"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response({"message": "Product added to cart"}, status=status.HTTP_200_OK)



class GoToCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        product_ids = list(cart_items.values_list("product__id", flat=True))
        return Response({"product_ids": product_ids}, status=status.HTTP_200_OK)
'''   
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
        payment_method = request.data.get("payment_method", "cod")

        try:
            with transaction.atomic():
                order = Order.objects.create(user=request.user, total_price=total_price, status="pending")
                OrderItem.objects.bulk_create([
                    OrderItem(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
                    for item in cart_items
                ])
                ShippingAddress.objects.create(
                    user=request.user, 
                    order=order,
                    name=request.data.get("name", request.user.username),
                    city=request.data.get("city", ""),
                    address=request.data.get("address", ""),
                    phone=request.data.get("phone", "")
                )
                transaction_id = str(uuid.uuid4())
                if payment_method == "cod":
                    payment = Payment.objects.create(
                        user=request.user,
                        order=order,
                        payment_method="COD",
                        transaction_id=transaction_id,
                        payment_status="Completed"
                    )
                    order.status = "shipped"
                    order.save()
                    return Response({"message": "Order placed successfully", "order_id": order.id}, status=status.HTTP_201_CREATED)

                elif payment_method in ["jazzcash", "easypaisa", "debitcard"]:
                    payload = {
                        "merchantCode": settings.TWOCHECKOUT_SELLER_ID,
                        "currency": "PKR",  # Pakistani Rupees
                        "amount": str(total_price),
                        "returnUrl": f"{settings.TWOCHECKOUT_RETURN_URL}?order_id={order.id}",
                        "cancelUrl": settings.TWOCHECKOUT_CANCEL_URL,
                        "orderNumber": str(order.id),
                        "paymentMethod": payment_method,  # JazzCash, EasyPaisa, or Debit Card
                        "lineItems": [{"name": f"Order #{order.id}", "price": total_price, "quantity": 1}],
                        "billingAddress": {
                            "name": request.user.name,
                            "email": request.user.email
                        }
                    }
                    headers = {
                        "Content-Type": "application/json",
                        "X-Avangate-Authentication": settings.TWOCHECKOUT_PRIVATE_KEY,
                    }
                    
                    response = requests.post(settings.TWOCHECKOUT_API_URL, json=payload, headers=headers)
                    if response.status_code == 201:
                        payment_data = response.json()
                        payment_url = payment_data.get("paymentUrl")
                        Payment.objects.create(
                            user=request.user,
                            order=order,
                            payment_method=payment_method,
                            transaction_id=transaction_id,
                            payment_status="Pending"
                        )

                        return Response({"message": "Redirect to 2Checkout for payment", "payment_url": payment_url}, status=status.HTTP_201_CREATED)
                    else:
                        order.status = "canceled"
                        order.save()
                        return Response({"error": "2Checkout payment initiation failed"}, status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response({"error": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"Order placement failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CheckoutWebhookView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        transaction_id = data.get("transaction_id")
        payment_status = data.get("status")
        order_id = data.get("order_id")
        
        try:
            with transaction.atomic():
                payment = Payment.objects.get(transaction_id=transaction_id, order__id=order_id)
                order = payment.order
                user = order.user

                if payment_status == "Completed":
                    payment.payment_status = "Completed"
                    order.status = "shipped"
                    ordered_products = order.orderitem_set.values_list('product_id', flat=True)
                    Cart.objects.filter(user=order.user, product_id__in=ordered_products).delete()
                    self.send_order_confirmation_email(user, order)
                    self.notify_delivery_partner(order)
                else:
                    payment.payment_status = "Failed"
                    order.status = "canceled"

                payment.save()
                order.save()

                return Response({"message": "Webhook processed successfully"}, status=status.HTTP_200_OK)

        except Payment.DoesNotExist:
            return Response({"error": "Invalid transaction ID or order ID"}, status=status.HTTP_400_BAD_REQUEST)

    def send_order_confirmation_email(self, user, order):
        """Send order confirmation email to the user."""
        subject = "Order Confirmation - IntelliWear"
        message = f"Dear {user.name},\n\nYour order #{order.id} has been placed successfully!\n\nOrder Details:\nTotal: ${order.total_price}\nStatus: {order.status}\n\nThank you for shopping with us!"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

    def notify_delivery_partner(self, order):
        """Notify the delivery partner via an API call."""
        delivery_data = {
            "order_id": order.id,
            "customer_name": order.user.name,
            "customer_address": order.shippingaddress.address,
            "customer_phone": order.shippingaddress.phone,
            "products": list(order.orderitem_set.values("product__name", "quantity")),
        }

        for _ in range(3):  
            response = requests.post(settings.DELIVERY_PARTNER_API_URL, json=delivery_data)
            if response.status_code == 200:
                return 
            time.sleep(2) 
'''

class OrderListView(APIView):
    permission_classes = [IsCustomerUser]
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
        product = get_object_or_404(Product, id=product_id)
        product_serializer = ProductDetailSerializer(product)

        reviews = Review.objects.filter(product_id=product_id).order_by('-created_at')
        paginator = ReviewPagination()
        paginated_reviews = paginator.paginate_queryset(reviews, request)
        review_serializer = ReviewSerializer(paginated_reviews, many=True)

        response_data = product_serializer.data
        response_data["reviews"] = review_serializer.data
        return paginator.get_paginated_response(response_data)

class CreateReviewView(APIView):
    permission_classes = [IsCustomerUser]

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        user = request.user
        # Prevent duplicate reviews
        if Review.objects.filter(product=product, user=user).exists():
            return Response({"error": "You have already reviewed this product."}, status=400)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, product=product)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)



    

#stripe Integration

# Set Stripe API Key
stripe.api_key = settings.STRIPE_SECRET_KEY
class PlaceOrderViewStripe(APIView):
    permission_classes = [IsCustomerUser]

    def post(self, request):
        selected_product_ids = request.data.get('product_ids', [])
        if not selected_product_ids:
            return Response({"error": "No products selected for order"}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = Cart.objects.filter(user=request.user, product__id__in=selected_product_ids)
        if not cart_items.exists():
            return Response({"error": "Selected products not in cart"}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.product.price * item.quantity for item in cart_items)
        payment_method = request.data.get("payment_method", "cod")
        try:
            with transaction.atomic():
                order = Order.objects.create(user=request.user, total_price=total_price, status="pending")
                OrderItem.objects.bulk_create([
                    OrderItem(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
                    for item in cart_items
                ])
                ShippingAddress.objects.create(
                    user=request.user,
                    order=order,
                    name=request.data.get("name", request.user.name),
                    city=request.data.get("city", ""),
                    address=request.data.get("address", ""),
                    phone=request.data.get("phone", "")
                )
                transaction_id = str(uuid.uuid4())

                if payment_method == "cod":
                    payment = Payment.objects.create(
                        user=request.user,
                        order=order,
                        payment_method="COD",
                        transaction_id=transaction_id,
                        payment_status="Completed"
                    )
                    order.status = "shipped"
                    order.save()
                    return Response({"message": "Order placed successfully", "order_id": order.id}, status=status.HTTP_201_CREATED)

                elif payment_method == "stripe":
                    # Create Stripe Checkout Session
                    checkout_session = stripe.checkout.Session.create(
                        payment_method_types=["card"],
                        line_items=[{
                            "price_data": {
                                "currency": "usd",
                                "product_data": {"name": f"Order #{order.id}"},
                                "unit_amount": int(total_price * 100),  # Convert to cents
                            },
                            "quantity": 1,
                        }],
                        mode="payment",
                        success_url=f"{settings.FRONTEND_URL}/customer/payment-success/",
                        cancel_url=f"{settings.FRONTEND_URL}/customer/payment-failed/",
                        metadata={"order_id": str(order.id)}
                    )

                    Payment.objects.create(
                        user=request.user,
                        order=order,
                        payment_method="stripe",
                        transaction_id=checkout_session.id,
                        payment_status="Pending"
                    )

                    return Response({"message": "Redirect to Stripe for payment", "payment_url": checkout_session.url}, status=status.HTTP_201_CREATED)

                else:
                    return Response({"error": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"Order placement failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class paymentFailView(APIView):
    def post(self, request):
        return Response({"message": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):

    def post(self, request):
        payload = request.body  # Raw bytes for signature verification
        sig_header = request.headers.get("Stripe-Signature")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)
        
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            metadata = session.get("metadata", {})

            order_id = metadata.get("order_id")
            if not order_id:
                return Response({"error": "Invalid order_id in metadata"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                with transaction.atomic():
                    payment = Payment.objects.select_related("order").get(transaction_id=session["id"])
                    order = payment.order  # Get related order

                    if str(order.id) != order_id:
                        return Response({"error": "Order ID mismatch"}, status=status.HTTP_400_BAD_REQUEST)

                    payment.payment_status = "Completed"
                    order.status = "in_process" 
                    payment.save()
                    order.save()
                    # Remove only the ordered items from the cart
                    ordered_products = order.items.values_list("product_id", flat=True)
                    Cart.objects.filter(user=order.user, product_id__in=ordered_products).delete()

            except Payment.DoesNotExist:
                return Response({"error": "Payment record not found"}, status=status.HTTP_200_OK)  # Return 200 to prevent retries

        return Response({"message": "Webhook processed successfully"}, status=status.HTTP_200_OK)
