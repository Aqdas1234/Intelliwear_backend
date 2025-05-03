from django.core.management.base import BaseCommand
from recommendation.models import Recommendation 
from recommendation.logic.singleton import get_cf_model

from django.contrib.auth import get_user_model
from adminApi.models import Product

User = get_user_model()

class Command(BaseCommand):
    help = "Generate and save product recommendations for all users"

    def handle(self, *args, **kwargs):
        cf = get_cf_model()
        users = User.objects.all()

        if cf is not None:
            for user in users:
                recommended_ids = cf.get_recommendations(user_id=user.id, num_recommendations=30)
                for pid in recommended_ids:
                    try:
                        product = Product.objects.get(id=pid)
                        Recommendation.objects.get_or_create(user=user, product=product)
                    except Product.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Product with ID {pid} does not exist. Skipping."))

            self.stdout.write(self.style.SUCCESS("Recommendations generated successfully."))
        