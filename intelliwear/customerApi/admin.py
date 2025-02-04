from django.contrib import admin
from .forms import CustomerForm
from .models import Customer
# Register your models here.

class CustomerAdmin(admin.ModelAdmin):
    #form = CustomerForm
    list_display = ('user', 'phone','email', 'address', 'profile_picture') 
    
    def email(self, obj):
        return obj.user.email 

admin.site.register(Customer)
