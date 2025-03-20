from django.utils import timezone
from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from adminApi.models import Product,Size
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator

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
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    username = None
    name = models.CharField(max_length=255, null=False, blank=False, default="Unknown")
    email = models.EmailField(unique=True) 
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = [] 
    is_superuser = models.BooleanField(default=False)  
    is_staff = models.BooleanField(default=False)
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.user_type == 'admin' and not self.is_superuser:
            raise ValidationError("Only superusers can assign the 'admin' type.")
        super().save(*args, **kwargs)

# Cart 
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=2)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE,) 
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product', 'size')  # Ensures size uniqueness

    def __str__(self):
        return f"{self.user.email} - {self.product.name} (Size: {self.size.size}) (Qty: {self.quantity})"

    def clean(self):
        if not self.size:
            raise ValidationError("Size is required for all products.")



class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=2)
    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} - {self.city}"

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=2)
    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50, choices=[
        ('easypaisa', 'Easypaisa'),
        ('jazzcash', 'JazzCash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('stripe', 'Stripe'),
        ('cod', 'Cash on Delivery')
    ])
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"Payment {self.id} - {self.user.email} - {self.payment_method}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_process', 'In Process'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=2 , related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    status_updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk:  
            old_order = Order.objects.get(pk=self.pk)
            if old_order.status != self.status:
                self.status_updated_at = now() 
        else:
            self.status_updated_at = now() 
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} by {self.user.email} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    return_status = models.CharField(
        max_length=20,
        choices=[
            ('Not Returned', 'Not Returned'),
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected')
        ],
        default='Not Returned'
    )

    def __str__(self):
        return f"{self.product.name} (Size: {self.size.size}) x {self.quantity}"

    def clean(self):
        if not self.size:
            raise ValidationError("Size is required for all products.")

# Review Model
class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  

    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name}"


class ReturnRequest(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="returns")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected')
        ],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return Request for {self.order_item.product.name} - {self.status}"
