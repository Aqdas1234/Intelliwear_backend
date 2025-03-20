from rest_framework import serializers
#from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from rest_framework.validators import UniqueValidator
from django.core.validators import MinValueValidator,MaxValueValidator
from django.conf import settings  
#from django.contrib.auth import get_user_model
from adminApi.serializers import ProductSerializer,MediaSerializer, SizeSerializer
from .models import ReturnRequest, User, Cart, Order, OrderItem, Review, ShippingAddress, Payment
from adminApi.models import Product, Size



class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])  
    password = serializers.CharField(write_only=True)  
    confirm_password = serializers.CharField(write_only=True)  
    total_delivered_orders = serializers.IntegerField(read_only=True)
    total_delivered_price = serializers.FloatField(read_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password','confirm_password','phone','address','profile_picture', 'user_type' , "total_delivered_orders", "total_delivered_price"]  

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User(**validated_data)
        user.set_password(validated_data['password'])  
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """Check if the email exists in the database."""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def create(self, validated_data):
        """Handle password reset email sending."""
        email = validated_data['email']
        user = User.objects.get(email=email)

        # Generate token and user ID encoding
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Frontend reset password URL
        frontend_url = f"{settings.FRONTEND_URL}/reset-password"
        reset_link = f"{frontend_url}/{uid}/{token}"

        # Send password reset email
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link below to reset your password:\n{reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return {"message": "Password reset email sent successfully."}


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"error": "Passwords do not match"})
        return data

class ProductListSerializer(serializers.ModelSerializer):
    sizes = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'image' , 'product_type']

    def get_sizes(self, obj):
        return SizeSerializer(obj.size_set.filter(quantity__gt=0), many=True).data

class ProductDetailSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, read_only=True)
    sizes = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'name', 'price','image', 'description', 'media','sizes']

    def get_sizes(self, obj):
        available_sizes = obj.size_set.filter(quantity__gt=0)  
        return SizeSerializer(available_sizes, many=True).data 
    
class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_name = serializers.ReadOnlyField(source='product.name')
    size = serializers.PrimaryKeyRelatedField(queryset=Size.objects.all()) 

    class Meta:
        model = Cart
        fields = ['id', 'product', 'product_name', 'size', 'quantity']

    def validate_size(self, value):
        if value is None:
            raise serializers.ValidationError("Size is required for all products.")
        return value

#place order
class OrderItemSerializer(serializers.ModelSerializer):
    size = serializers.PrimaryKeyRelatedField(queryset=Size.objects.all())  # Required input field
    product_name = serializers.CharField(source='product.name', read_only=True)
    return_status = serializers.CharField(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id','product','product_name', 'size', 'quantity', 'price','return_status']

    def validate_size(self, value):
        if value is None:
            raise serializers.ValidationError("Size is required for all products.")
        return value


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['name','city', 'address', 'phone']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_method', 'transaction_id', 'payment_status']


class OrderListSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id','user','total_price','status','items','created_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = serializers.SerializerMethodField()
    payment = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'status', 'created_at', 'items', 'shipping_address', 'payment']
    def get_shipping_address(self, obj):
        shipping = ShippingAddress.objects.filter(order=obj).first()
        return ShippingAddressSerializer(shipping).data if shipping else None

    def get_payment(self, obj):
        payment = Payment.objects.filter(order=obj).first()
        return PaymentSerializer(payment).data if payment else None

class ReviewSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at']

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True, help_text="ID of the product to add to the cart")
    size_id = serializers.IntegerField(required=True, help_text="ID of the size variant for the product")
    quantity = serializers.IntegerField(default=1, min_value=1, help_text="Quantity of the product to add (default: 1)")


class ReturnRequestSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="order_item.product.name", read_only=True)
    size = serializers.CharField(source="order_item.size.size", read_only=True)  
    quantity = serializers.IntegerField(source="order_item.quantity", read_only=True)
    price = serializers.DecimalField(source="order_item.price", max_digits=10, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = ReturnRequest
        fields = ["id", "order_item", "product_name", "size", "quantity", "price", "reason", "status", "created_at"]


'''


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])  
    password = serializers.CharField(write_only=True)  
    confirm_password = serializers.CharField(write_only=True)  

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'confirm_password']  

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User(**validated_data)
        user.set_password(validated_data['password'])  
        user.save()
        return user

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = ['user', 'phone', 'address', 'profile_picture', 'user_type']

    def validate_user_type(self, value):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            if value == 'admin' and not request.user.is_superuser:
                raise serializers.ValidationError("Only superusers can assign the 'admin' type.")
        return value

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)  
        if user_serializer.is_valid(raise_exception=True):  
            user = user_serializer.save()
        customer = Customer.objects.create(user=user, **validated_data)
        return customer

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        user = instance.user

        if user_data:
            password = user_data.pop('password', None)
            confirm_password = user_data.pop('confirm_password', None)

            if password:
                if not confirm_password or password != confirm_password:
                    raise serializers.ValidationError({"password": "Passwords do not match."})
                user.set_password(password)

            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

#Change Password Serializer
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
    
#forgot Password
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def send_password_reset_email(self, request):
        """Send email with reset link"""
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))  # Encode user ID
        token = default_token_generator.make_token(user)  # Generate token
        # reset_link = request.build_absolute_uri(
        #     reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})
        # )
        frontend_url = "http://localhost:5173/reset-password"
        reset_link = f"{frontend_url}/{uid}/{token}"


        send_mail(
            subject="Password Reset Request",
            message=f"Click the link below to reset your password:\n{reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"error": "Passwords do not match"})
        return data



from adminApi.models import Product, Media

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['file', 'media_type']


class ProductListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'image']

    def get_image(self, obj):
        first_image = obj.media.filter(media_type='IMAGE').first()
        return first_image.file.url if first_image else None


class ProductDetailSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'media']


#Cart Serializer
class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'product', 'product_name', 'quantity']

    def get_product_name(self, obj):
        return obj.product.name if obj.product else None

#place order
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['name', 'city', 'address', 'phone']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_method', 'transaction_id', 'payment_status']


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField()  # Display customer email instead of ID
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = serializers.SerializerMethodField()
    payment = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'total_price', 'status', 'created_at', 'items', 'shipping_address', 'payment']
        read_only_fields = ['customer']

    def get_shipping_address(self, obj):
        shipping = ShippingAddress.objects.filter(order=obj).first()
        return ShippingAddressSerializer(shipping).data if shipping else None

    def get_payment(self, obj):
        payment = Payment.objects.filter(order=obj).first()
        return PaymentSerializer(payment).data if payment else None

# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)  # Display customer email instead of ID
    product = serializers.StringRelatedField(read_only=True)  # Display product name instead of ID
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'customer', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at', 'customer', 'product']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
'''