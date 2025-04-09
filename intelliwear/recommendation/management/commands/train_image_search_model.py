from django.core.management.base import BaseCommand
from adminApi.models import Product
from recommendation.logic.singleton import get_image_search_model  


class Command(BaseCommand):
    help = "Train and add products to the image search model"

    def handle(self, *args, **kwargs):
        image_search_model = get_image_search_model()  

        products = Product.objects.all()
        for product in products:
            try:
                image_url = 'https://res.cloudinary.com/doz6xoqzu/'
                image_url += product.image.public_id  # Cloudinary URL
                
                product_id = str(product.id)  
                image_search_model.addProduct(product_id, image_url)
                
            except Exception as e:
                print(f"Error processing product {product.id}: {e}")

        print("Image search model training completed!")
