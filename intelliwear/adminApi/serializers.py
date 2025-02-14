from rest_framework import serializers
#from django.contrib.auth.models import User
from .models import Product,Size,Media,Color,Carousel
from django.contrib.auth.password_validation import validate_password
'''
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
'''    

#product 


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'file', 'media_type']
    
    def validate(self, data):
        product = data.get("product")
        media_count = Media.objects.filter(product=product).count()

        if media_count >= 4:
            raise serializers.ValidationError("You can only upload a maximum of 4 additional media files per product.")

        return data

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
        fields = ['id', 'name', 'description','stock', 'price', 'product_type','image', 'sizes', 'colors', 'media', 'gender', 'created_at', 'updated_at']

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
            size_obj, _ = Size.objects.get_or_create(**size)  
            product.sizes.add(size_obj)

        # Create Color objects
        for color in colors_data:
            color_obj, _ = Color.objects.get_or_create(**color)  
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
        
        instance.media.all().delete()
        for media in media_data:
            Media.objects.create(product=instance, **media)

        instance.sizes.clear()
        for size in sizes_data:
            size_obj, _ = Size.objects.get_or_create(**size)
            instance.sizes.add(size_obj)

        instance.colors.clear()
        for color in colors_data:
            color_obj, _ = Color.objects.get_or_create(**color)
            instance.colors.add(color_obj)

        return instance
    
class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = '__all__'