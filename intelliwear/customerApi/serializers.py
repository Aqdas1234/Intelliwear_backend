from rest_framework import serializers
from .models import Customer,Cart,Order,OrderItem,Review,ReviewImage,ShippingAddress,Payment
#from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from rest_framework.validators import UniqueValidator
from django.conf import settings  
from django.contrib.auth import get_user_model


User = get_user_model() 

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])  
    password = serializers.CharField(write_only=True) 
    confirm_password = serializers.CharField(write_only=True)  

    class Meta:
        model = User
        fields = ['email',  'name', 'password','confirm_password']
        extra_kwargs = {'email': {'required': True, 'allow_blank': False, 'unique': True}}
    '''
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    '''
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
        if request and getattr(request, 'user', None):
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
            confirm_password = user_data.pop('confirm_password', None)  
            password = user_data.get('password', None)
            if password:
                if confirm_password is None or password != confirm_password:
                    raise serializers.ValidationError({"password": "Passwords do not match."})
                user.set_password(password)  
        
            updated = False
            for attr, value in user_data.items():
                if getattr(user, attr) != value:  
                    setattr(user, attr, value)
                    updated = True

            if updated or password:  
                user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


  

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
        reset_link = request.build_absolute_uri(
            reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})
        )

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
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = Cart
        fields = ['id', 'product', 'product_name', 'quantity']

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
    
#Review
class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    images = ReviewImageSerializer(many=True, read_only=True)  # Nested images

    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rating', 'comment', 'created_at', 'images']

class ReviewCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Review
        fields = ['id', 'product', 'rating', 'comment', 'images']

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        review = Review.objects.create(**validated_data)
        
        for image in images:
            ReviewImage.objects.create(review=review, image=image)

        return review