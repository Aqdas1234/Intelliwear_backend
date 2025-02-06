from django.contrib import admin
from .models import Customer

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'phone', 'address', 'profile_picture', 'user_type')  
    list_filter = ('user_type',)  # Filter by user type
    search_fields = ('user__username', 'user__email', 'phone', 'address')  # Improve search functionality

    def email(self, obj):
        return obj.user.email  
    email.admin_order_field = 'user__email'  # Allow sorting by email
    email.short_description = 'Email'  

    def get_readonly_fields(self, request, obj=None):
        
        if not request.user.is_superuser:
            return ('user_type',)
        return ()

admin.site.register(Customer, CustomerAdmin)
