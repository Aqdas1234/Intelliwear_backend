from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ReturnRequest, User, Cart, Order, OrderItem, Review, Payment, ShippingAddress

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id','email', 'name', 'phone', 'is_staff', 'is_superuser', 'user_type')
    search_fields = ('email', 'name', 'phone')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # Default fields for login
        ('Personal Info', {'fields': ('name', 'phone', 'address', 'user_type', 'profile_picture')}),  # Personal details
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),  # Permissions
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),  # Dates for login
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type')}
        ),
    )

# Cart
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'product', 'size', 'quantity', 'added_at')
    search_fields = ('user__email', 'product__name')
    list_filter = ('size',)

# Order & Order Item
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'id')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'size', 'product', 'quantity', 'price','return_status')
    search_fields = ('order__id', 'product__name')
    list_filter = ('size',) 

# Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    search_fields = ('user__email', 'product__name', 'comment')
    list_filter = ('rating', 'created_at')

# Shipping Address
@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'name','city','address', 'phone')
    search_fields = ('user__email', 'name','city','address', 'phone')
    list_filter = ('city',)

# Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'payment_method', 'transaction_id', 'payment_status')
    search_fields = ('user__email', 'transaction_id')
    list_filter = ('payment_status', 'payment_method')


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "order_item", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_item__product__name", "user__email")
    ordering = ("-created_at",)