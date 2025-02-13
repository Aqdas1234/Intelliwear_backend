from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.core.exceptions import ValidationError
from adminApi.models import Product

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not email:
            raise ValueError("Superusers must have an email address")
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    name = models.CharField(max_length=255, null=False, blank=False, default="Unknown")
    email = models.EmailField(unique=True) 
    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = [] 
    is_superuser = models.BooleanField(default=False)  
    is_staff = models.BooleanField(default=False)
    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Customer(models.Model):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer")
    phone = models.CharField(max_length=15,unique=True)
    address = models.TextField(blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    '''
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    '''
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True,null=True)

    def __str__(self):
        return self.user.email 
    
    def save(self, *args, **kwargs):
        if self.user_type == 'admin' and not self.user.is_superuser:
            raise ValidationError("Only superusers can assign the 'admin' type.")
        super().save(*args, **kwargs)




#Cart 
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  

    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.quantity})"