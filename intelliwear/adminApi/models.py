from django.db import models
import uuid
#from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import os
from django.conf import settings
from cloudinary.models import CloudinaryField
from cloudinary.uploader import destroy


class Media(models.Model):
    MEDIA_TYPES = [
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
    ]
    id = models.AutoField(primary_key=True)
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='media')  # One-to-Many
    #file = models.FileField(upload_to='product_media/', blank=True, null=True)
    file = CloudinaryField('image', blank=True, null=True,folder="product_media")
    #media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    #created_at = models.DateTimeField(auto_now_add=True)
    def clean(self):
        if self.product.media.count() >= 4:  
            raise ValidationError("You can only upload a maximum of 4 additional media files per product.")

    def save(self, *args, **kwargs):
        self.clean() 
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.file.name}"


'''
class Color(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    #hex_code = models.CharField(max_length=7, unique=True, help_text="Hex color code (e.g., #FF5733)")

    def __str__(self):
        return self.name
'''

class Product(models.Model):
    PRODUCT_TYPES = [
        ('CLOTHES', 'Clothes'),
        ('SHOES', 'Shoes'),
        ('ACCESSORIES', 'Accessories'),
    ]

    GENDER_CHOICES = [
        ('A', 'All'),
        ('M', 'Men'),
        ('W', 'Women'),
        ('C', 'Children'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    #stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_type = models.CharField(max_length=12, choices=PRODUCT_TYPES)
    #image = models.ImageField(upload_to='product_main_images/', blank=False, null=False,default='product_media/images.jpeg')
    image = CloudinaryField('image',folder="product_main_images", blank=False, null=False)
    #colors = models.ManyToManyField(Color, blank=True, related_name='products')  # Many-to-Many (valid)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """Custom validation for required image field"""
        if not self.image:
            raise ValidationError("Product image is required.")

    def __str__(self):
        return f"{self.get_product_type_display()} - {self.name} ({self.get_gender_display()})"

    def delete(self, *args, **kwargs):
        if self.image:
            destroy(self.image.public_id)  # Deletes from Cloudinary
            super().delete(*args, **kwargs)
        '''
        if self.image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(self.image))
            if os.path.isfile(image_path):
                os.remove(image_path)
        super().delete(*args, **kwargs)        
        '''


class Size(models.Model):
    id = models.AutoField(primary_key=True)
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')  # One-to-Many relation
    size = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0)  # Stock for this size

    def __str__(self):
        return f"{self.size} - {self.product.name} (Stock: {self.quantity})" 

    class Meta:
        constraints = [models.UniqueConstraint(fields=['product', 'size'], name='unique_product_size')]
        
class Carousel(models.Model):
    title = models.CharField(max_length=255)
    #image = models.ImageField(upload_to='carousel_images/')
    image = CloudinaryField('image', folder="carousel_images")
    #link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        if self.image:
            destroy(self.image.public_id)  # Deletes from Cloudinary
            super().delete(*args, **kwargs)
        '''
        if self.image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(self.image))
            if os.path.isfile(image_path):
                os.remove(image_path)
        super().delete(*args, **kwargs)    '
        '''