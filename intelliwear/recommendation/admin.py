
from django.contrib import admin
from .models import SimilarProduct,Recommendation

@admin.register(SimilarProduct)
class SimilarProductAdmin(admin.ModelAdmin):
    list_display = ('id','product', 'similar_product')
    search_fields = ('product__name', 'similar_product__name')

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'recommended_at', 'updated_at')
    search_fields = ('user__username', 'product__name') 