
from django.contrib import admin
from .models import SimilarProduct

@admin.register(SimilarProduct)
class SimilarProductAdmin(admin.ModelAdmin):
    list_display = ('id','product', 'similar_product')
    search_fields = ('product__name', 'similar_product__name')