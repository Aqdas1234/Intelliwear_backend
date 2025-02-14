from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.
'''
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

'''





class Media(models.Model):
    MEDIA_TYPES = [
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='media')  # One-to-Many
    file = models.FileField(upload_to='product_media/', blank=True, null=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    #created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.media_type} - {self.file.name}"


class Size(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    size = models.CharField(max_length=50, unique=True)  

    def __str__(self):
        return self.size


class Color(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    #hex_code = models.CharField(max_length=7, unique=True, help_text="Hex color code (e.g., #FF5733)")

    def __str__(self):
        return self.name


class Product(models.Model):
    PRODUCT_TYPES = [
        ('CLOTHES', 'Clothes'),
        ('SHOES', 'Shoes'),
        ('ACCESSORIES', 'Accessories'),
    ]

    GENDER_CHOICES = [
        ('M', 'Men'),
        ('W', 'Women'),
        ('C', 'Children'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_type = models.CharField(max_length=12, choices=PRODUCT_TYPES)
    sizes = models.ManyToManyField(Size, blank=True, related_name='products')  # Many-to-Many (valid)
    colors = models.ManyToManyField(Color, blank=True, related_name='products')  # Many-to-Many (valid)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_product_type_display()} - {self.name} ({self.get_gender_display()})"
    
class Carousel(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='carousel_images/')
    #link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title