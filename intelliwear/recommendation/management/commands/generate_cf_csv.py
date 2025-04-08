from django.core.management.base import BaseCommand
from customerApi.models import OrderItem, Cart
from django.contrib.auth import get_user_model
import csv
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates cf_data.csv for collaborative filtering model'

    def handle(self, *args, **kwargs):
        output_folder = 'recommendation/data/'
        output_file = os.path.join(output_folder, 'data.csv')

        os.makedirs(output_folder, exist_ok=True)

        with open(output_file, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['buyer', 'product', 'weight'])

            buyers_with_orders = set(OrderItem.objects.values_list('order__user_id', flat=True))

            for item in OrderItem.objects.select_related('order', 'product'):
                writer.writerow([item.order.user.id, item.product.id, 1.0])

            for item in Cart.objects.select_related('user', 'product'):
                if item.user.id in buyers_with_orders:
                    writer.writerow([item.user.id, item.product.id, 0.5])

        self.stdout.write(self.style.SUCCESS(f'cf_data.csv generated at {output_file}'))
