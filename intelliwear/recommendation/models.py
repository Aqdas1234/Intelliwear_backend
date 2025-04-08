from django.db import models
from adminApi.models import Product 
from django.contrib.auth import get_user_model
User = get_user_model()

class SimilarProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='base_products')
    similar_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='similar_to_products')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} → {self.similar_product.name}"



class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    recommended_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recommendation for user {self.user.id} (ID) - Product {self.product.id}"
