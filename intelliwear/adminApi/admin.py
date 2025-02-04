from django.contrib import admin
from .models import SellerProfile
# Register your models here.
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'store_name', 'phone_number', 'updated_at')

admin.site.register(SellerProfile, SellerProfileAdmin)


