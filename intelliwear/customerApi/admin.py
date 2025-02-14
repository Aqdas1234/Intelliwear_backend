from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Customer,Cart,Order,OrderItem

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email',  'name', 'is_staff', 'is_superuser')
    search_fields = ('email', 'name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user','get_user_id', 'get_email', 'phone', 'address', 'profile_picture', 'user_type')  
    list_filter = ('user_type',)  
    search_fields = ('user__email', 'phone', 'address')  

    def get_email(self, obj):
        return obj.user.email  
    get_email.admin_order_field = 'user__email'  
    get_email.short_description = 'Email'  

    def get_user_id(self, obj):
        return obj.user.id
    get_user_id.admin_order_field = 'user__id'  
    get_user_id.short_description = 'User ID'

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('user_type','get_user_id')
        return ['get_user_id']

admin.site.register(Customer, CustomerAdmin)

#cart
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'added_at')  
    search_fields = ('user__email', 'product__name')

#order & order item
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')