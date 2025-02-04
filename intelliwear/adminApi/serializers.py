from rest_framework import serializers
from django.contrib.auth.models import User
from .models import SellerProfile
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