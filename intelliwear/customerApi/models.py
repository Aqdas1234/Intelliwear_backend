from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="customer")
    phone = models.CharField(max_length=15, blank=True, null=True,unique=True)
    address = models.TextField(blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    '''
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    '''
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True,null=True)

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        # Ensure that only superusers can assign the 'admin' type
        if self.user_type == 'admin' and not self.user.is_superuser:
            raise ValueError("Only superusers can assign the 'admin' type.")
        super().save(*args, **kwargs)
