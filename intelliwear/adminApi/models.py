from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.

#Seller Profile Model
class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile') # Link to Django's User model
    store_name = models.CharField(max_length=255, default="IntelliWear")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='seller_profile/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Seller"
