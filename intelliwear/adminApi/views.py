from django.shortcuts import render
from django.conf import settings
import pandas as pd
from recommendation.logic.recommendation import CBModel
#from django.contrib.auth.models import User
from rest_framework import viewsets, status , filters,generics
from customerApi.serializers import ReturnRequestSerializer, UserSerializer , ReviewSerializer
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
from customerApi.serializers import OrderSerializer
from customerApi.models import Order, ReturnRequest , Review
from django.template.loader import render_to_string
from django.core.mail import send_mail
from recommendation.logic.singleton import get_cb_model,get_cf_model,get_image_search_model,get_nlp_model

from django.db.models import Count, Sum, Case, When, IntegerField, FloatField
from django.utils.timezone import now
from datetime import timedelta


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
        users = User.objects.filter(user_type="customer").annotate(
            total_delivered_orders=Count(
                Case(
                    When(orders__status="delivered", then=1),
                    output_field=IntegerField(),
                )
            ),
            total_delivered_price=Sum(
                Case(
                    When(orders__status="delivered", then="orders__total_price"),
                    output_field=FloatField(),
                )
            ),
        ).order_by("-created_at")

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
    
    def perform_create(self, serializer):
        instance = serializer.save()
        
        # Convert instance to DataFrame format required by addProducts
        
        data = {
            'ProductID': [str(instance.id)],
            'ProductName': [instance.name],
            'Description': [instance.description],
            'ProductBrand':[''],
            'Price (INR)': [instance.price],
            'Type': [instance.product_type],
            'Gender': [instance.gender],
            'Status': ['active'],
        }
        df = pd.DataFrame(data)
        cb_model = get_cb_model()
        if cb_model is not None:
            cb_model.addProducts(df)

        nlp_model = get_nlp_model()
        if nlp_model is not None:
            nlp_model.addProducts(df)

        img_model = get_image_search_model()
        if img_model is not None:
            image_url = 'https://res.cloudinary.com/doz6xoqzu/'
            image_url += instance.image.public_id  
            img_model.addProduct(str(instance.id), image_url)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        product_id = str(instance.id)
        cb_model = get_cb_model()
        if cb_model is not None:
            cb_model.delete(product_id)
            
        nlp_model = get_nlp_model()
        if nlp_model is not None:
            nlp_model.delete(product_id)

        img_model = get_image_search_model()
        if img_model is not None:
            img_model.deleteProduct(instance.id)
        #cf_model = get_cf_model()
        #if cf_model is not None:
        #    cf_model.delete_product(product_id)
        return super().destroy(request, *args, **kwargs)


@extend_schema(tags=["Carousel"])
class CarouselViewSet(viewsets.ModelViewSet):
    queryset = Carousel.objects.all().order_by("-created_at")
    serializer_class = CarouselSerializer
    parser_classes = (MultiPartParser, FormParser) 

    def get_permissions(self):
        if self.action == "list": 
            return [AllowAny()]
        return [IsSuperUser()]  
    

@extend_schema(tags=["Admin - OrdersListView"])
class AdminOrderListView(APIView):
    permission_classes = [IsSuperUser]
    pagination_class = MyLimitOffsetPagination 

    @extend_schema(
        parameters=[
            OpenApiParameter(name="limit", description="Number of results per page", required=False, type=int),
            OpenApiParameter(name="offset", description="Pagination offset", required=False, type=int),
            OpenApiParameter(name="status", description="Filter orders by status", required=False, type=str),
        ],
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request):
        status_filter = request.query_params.get("status")

        orders = Order.objects.all().order_by("-created_at")

        if status_filter:  
            orders = orders.filter(status=status_filter) 

        paginator = self.pagination_class()  
        paginated_orders = paginator.paginate_queryset(orders, request)
        serializer = OrderSerializer(paginated_orders, many=True)
        return paginator.get_paginated_response(serializer.data)    
    
@extend_schema(tags=["Admin - UpdateOrderStatusView"])
class AdminUpdateOrderStatusView(APIView):
    permission_classes = [IsSuperUser]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get("status")

        valid_statuses = ["pending", "in_process", "shipped", "delivered"]
        if new_status not in valid_statuses:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()

        if new_status in ["pending", "in_process"]:
            return Response({"message": f"Order status updated to {new_status} successfully."}, status=status.HTTP_200_OK)

        user_email = order.user.email
        email_subject = f"Your Order #{order.id} is now {new_status.capitalize()}"
        order_items = order.items.all()

        email_context = {
            "user": order.user,
            "order": order
        }

        if new_status == "shipped":
            template_name = "emails/order_shipped.html"
            email_context.update({
                "shipping_carrier": "TCS",
                "tracking_number": "12345",
                "order_items": order_items,
                "total_price": order.total_price
            })

        elif new_status == "delivered":
            template_name = "emails/order_delivered.html"
            email_context.update({
                "products_with_review_links": [
                    {
                        "name": item.product.name,
                        "review_link": f"{settings.FRONTEND_URL}/product/{item.product.id}?source=email"
                    }
                    for item in order_items
                ]
            })

        email_body = render_to_string(template_name, email_context)

        send_mail(
            email_subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
            html_message=email_body
        )

        return Response({"message": f"Order status updated to {new_status} and email sent."}, status=status.HTTP_200_OK)


class AdminAnalyticsView(APIView):
    def get(self, request):
        today = now().date()
        filter_type = request.GET.get("filter", "last_7_days")  

        if filter_type == "last_7_days":
            start_date = today - timedelta(days=7)
        elif filter_type == "last_14_days":
            start_date = today - timedelta(days=14)
        elif filter_type == "last_30_days":
            start_date = today - timedelta(days=30)
        elif filter_type == "last_90_days":
            start_date = today - timedelta(days=90)
        elif filter_type == "all_time":
            start_date = None  
        else:
            return Response({"error": "Invalid filter type"}, status=400)

        if start_date:
            orders = Order.objects.filter(created_at__date__gte=start_date)
        else:
            orders = Order.objects.all()

        delivered_orders = orders.filter(status="delivered")
        
        total_sales = delivered_orders.aggregate(total=Sum("total_price"))["total"] or 0
        total_orders = orders.count()
        delivered_orders_count = delivered_orders.count()
        avg_order_value = total_sales / delivered_orders_count if delivered_orders_count > 0 else 0

        today_sales = delivered_orders.filter(status_updated_at__date=today).aggregate(total=Sum("total_price"))["total"] or 0

        order_status_counts = orders.values("status").annotate(count=Count("id"))
        order_status_data = {
            "cancelled": 0,
            "shipped": 0,
            "delivered": 0,
            "in_process": 0
        }
        for entry in order_status_counts:
            order_status_data[entry["status"]] = entry["count"]

        return Response({
            "start_date": start_date if start_date else "All Time",
            "end_date": today,
            "total_sales": total_sales,
            "today_sales": today_sales,
            "total_orders": total_orders,
            "avg_order_value": avg_order_value,
            "order_status_data": order_status_data,  
        })


class AdminReturnRequestListView(generics.ListAPIView):
    serializer_class = ReturnRequestSerializer
    permission_classes = [IsSuperUser]
    queryset = ReturnRequest.objects.all()



class AdminReturnRequestView(generics.RetrieveUpdateAPIView):
    serializer_class = ReturnRequestSerializer
    permission_classes = [IsSuperUser]
    queryset = ReturnRequest.objects.all()

    def update(self, request, *args, **kwargs):
        """Admin can approve/reject return requests"""
        instance = self.get_object()
        new_status = request.data.get("status")

        if new_status not in ["Approved", "Rejected"]:
            return Response({"error": "Invalid status. Choose 'Approved' or 'Rejected'."},
                            status=status.HTTP_400_BAD_REQUEST)

        instance.status = new_status
        instance.save()

        instance.order_item.return_status = new_status
        instance.order_item.save()
        self.send_email_to_customer(instance)

        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)

    def send_email_to_customer(self, return_request):
        user_email = return_request.user.email
        subject = f"Return Request Update: {return_request.status}"

        context = {
            "user": return_request.user.name,
            "order_item": return_request.order_item,
        }
        if return_request.status == "Approved":
            template_name = "emails/return_request_approved.html"
        else:
            template_name = "emails/return_request_rejected.html"

        email_body = render_to_string(template_name, context)

        send_mail(
            subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
            html_message=email_body
        )
class AdminReviewListView(APIView):
    permission_classes = [IsSuperUser]  
    pagination_class = MyLimitOffsetPagination 

    def get(self, request):
        reviews = Review.objects.all().order_by('-created_at')  
        
        paginator = self.pagination_class() 
        paginated_reviews = paginator.paginate_queryset(reviews, request) 
        
        serializer = ReviewSerializer(paginated_reviews, many=True)  
        return paginator.get_paginated_response(serializer.data)  

    def delete(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)  
        review.delete()  
        return Response({"message": "Review deleted successfully"}, status=status.HTTP_204_NO_CONTENT)    