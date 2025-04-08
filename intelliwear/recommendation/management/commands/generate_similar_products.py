from django.core.management.base import BaseCommand
from adminApi.models import Product
from recommendation.models import SimilarProduct  
from recommendation.logic.singleton import get_cb_model

class Command(BaseCommand):
    help = "Generate and save similar products"

    def handle(self, *args, **kwargs):
        cb = get_cb_model()
        products = Product.objects.all()

        for product in products:
            similar_ids = cb.find_similar(str(product.id), k=5)

            for sim_id in similar_ids:
                try:
                    similar_product = Product.objects.get(id=sim_id)
                    SimilarProduct.objects.get_or_create(
                        product=product,
                        similar_product=similar_product
                    )
                except Product.DoesNotExist:
                    continue 
