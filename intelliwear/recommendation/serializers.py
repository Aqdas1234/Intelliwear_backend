from rest_framework import serializers
from .models import SimilarProduct
from adminApi.models import Product  

class SimilarProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimilarProduct
        fields = ['id', 'product', 'similar_product']