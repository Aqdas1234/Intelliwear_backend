from django.contrib import admin
from .models import Size,Media,Product,Color,Carousel
# Register your models here.
'''
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'store_name', 'phone_number', 'updated_at')

admin.site.register(SellerProfile, SellerProfileAdmin)
'''

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'price','image', 'gender', 'created_at', 'updated_at')
    search_fields = ('name', 'product_type')
    list_filter = ('product_type', 'gender', 'created_at')
    filter_horizontal = ('sizes', 'colors')  # Allow many-to-many selection in admin
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('product', 'media_type', 'file', )
    list_filter = ('media_type', )
    search_fields = ('product__name',)

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('size',)
    search_fields = ('size',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )

@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'created_at')
    search_fields = ('title',)