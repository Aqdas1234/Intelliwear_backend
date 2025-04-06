from django.db import models
from adminApi.models import Product  

class SimilarProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='base_products')
    similar_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='similar_to_products')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} → {self.similar_product.name}"
