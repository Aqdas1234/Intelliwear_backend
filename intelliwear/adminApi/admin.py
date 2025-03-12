from django.contrib import admin
from .models import Size,Media,Product,Carousel
# Register your models here.
'''
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'store_name', 'phone_number', 'updated_at')

admin.site.register(SellerProfile, SellerProfileAdmin)
'''
class MediaInline(admin.TabularInline):  
    model = Media  
    extra = 1 

class SizeInline(admin.TabularInline):
    model = Size
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'product_type', 'price', 'image', 'gender', 'created_at', 'updated_at')
    search_fields = ('name', 'product_type')
    list_filter = ('product_type', 'gender', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MediaInline,SizeInline]
    

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('id','product' , 'file', )
    #list_filter = ('media_type', )
    search_fields = ('product__name',)

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('id','size', 'product') 
    search_fields = ('size', 'product__name')
    list_filter = ('size', 'product')
    
'''
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
'''

@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'created_at')
    search_fields = ('title',)