import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from adminApi.models import Product

class Command(BaseCommand):
    help = "Export all products to a CSV file"

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'recommendation/data/products.csv')

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ProductID', 'ProductName', 'Description','ProductBrand', 'Price (INR)', 'Type', 'Gender', 'Status'])

           
            products = Product.objects.all()
            for product in products:
                writer.writerow([
                    product.id,
                    product.name,
                    product.description,
                    '',
                    product.price,
                    product.get_product_type_display(),
                    product.get_gender_display(),
                    'active'  
                ])

        self.stdout.write(self.style.SUCCESS(f'Successfully exported {products.count()} products to {file_path}'))
