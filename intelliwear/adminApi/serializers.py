from rest_framework import serializers
from django.contrib.auth.models import User
from .models import SellerProfile,Product,Size,Media,Color
from django.contrib.auth.password_validation import validate_password

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])


class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = ['store_name', 'phone_number', 'address', 'profile_picture', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    seller_profile = SellerProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'email', 'seller_profile']

    def update(self, instance, validated_data):
        seller_data = validated_data.pop('seller_profile', {})
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # Update Seller Profile
        seller_profile, _ = SellerProfile.objects.get_or_create(user=instance)
        seller_profile.store_name = seller_data.get('store_name', seller_profile.store_name)
        seller_profile.phone_number = seller_data.get('phone_number', seller_profile.phone_number)
        seller_profile.address = seller_data.get('address', seller_profile.address)
        seller_profile.profile_picture = seller_data.get('profile_picture', seller_profile.profile_picture)
        seller_profile.save()

        return instance
    
#product 


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'file', 'media_type']

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'size']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name' ]

class ProductSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, required=False)  # Allow nested media
    sizes = SizeSerializer(many=True, required=False)   # Allow nested sizes
    colors = ColorSerializer(many=True, required=False) # Allow nested colors

    class Meta:
        model = Product
        fields = ['id', 'name', 'description','stock', 'price', 'product_type', 'sizes', 'colors', 'media', 'gender', 'created_at', 'updated_at']

    def create(self, validated_data):
        media_data = validated_data.pop('media', [])
        sizes_data = validated_data.pop('sizes', [])
        colors_data = validated_data.pop('colors', [])
        
        product = Product.objects.create(**validated_data)

        # Create Media objects
        for media in media_data:
            Media.objects.create(product=product, **media)

        # Create Size objects
        for size in sizes_data:
            size_obj, _ = Size.objects.get_or_create(**size)  # Avoid duplicate sizes
            product.sizes.add(size_obj)

        # Create Color objects
        for color in colors_data:
            color_obj, _ = Color.objects.get_or_create(**color)  # Avoid duplicate colors
            product.colors.add(color_obj)

        return product

    def update(self, instance, validated_data):
        media_data = validated_data.pop('media', [])
        sizes_data = validated_data.pop('sizes', [])
        colors_data = validated_data.pop('colors', [])

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update Media (Clear old media and add new)
        instance.media.all().delete()
        for media in media_data:
            Media.objects.create(product=instance, **media)

        # Update Sizes (Clear old sizes and add new)
        instance.sizes.clear()
        for size in sizes_data:
            size_obj, _ = Size.objects.get_or_create(**size)
            instance.sizes.add(size_obj)

        # Update Colors (Clear old colors and add new)
        instance.colors.clear()
        for color in colors_data:
            color_obj, _ = Color.objects.get_or_create(**color)
            instance.colors.add(color_obj)

        return instance
