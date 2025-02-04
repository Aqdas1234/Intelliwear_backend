from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="customer")
    phone = models.CharField(max_length=15, blank=True, null=True,unique=True)
    address = models.TextField(blank=True, null=True)
    '''
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    '''
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True,null=True)

    def __str__(self):
        return self.user.username
