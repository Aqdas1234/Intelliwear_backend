from django.db.models.signals import post_save
from django.dispatch import receiver
from customerApi.models import Cart, OrderItem
from recommendation.logic.singleton import get_cf_model 
from adminApi.models import Product
from recommendation.models import Recommendation 


@receiver(post_save, sender=Cart)
def cart_item_added(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        product_id = instance.product.id  
        weight = 0.5  
        has_order = OrderItem.objects.filter(order__user=user).exists()
        if has_order:
            cf_model = get_cf_model()
            if cf_model is not None:
                cf_model.add_interaction(buyer_id=user.id, product_id=product_id, weight=weight)
            else:
                print("Error: Collaborative filtering model (cf_model) is None")
        else:
            print(f"User {user.id} has not placed any order or does not have an OrderItem yet.")


@receiver(post_save, sender=OrderItem)
def order_item_added(sender, instance, created, **kwargs):
    if created:
        user = instance.cart.user
        product_id = instance.product.id 
        weight = 1.0  
        cf_model = get_cf_model()
        if cf_model is not None:
            cf_model.add_interaction(buyer_id=user.id, product_id=product_id, weight=weight)
            recommended_ids = cf_model.get_recommendations(user_id=user.id, num_recommendations=30)
            for pid in recommended_ids:
                try:
                    product = Product.objects.get(id=pid)
                    Recommendation.objects.get_or_create(user=user, product=product)
                except Product.DoesNotExist:
                    print(f"Warning: Product with ID {pid} does not exist. Skipping.")

        else:
            print("Error: Collaborative filtering model (cf_model) is None")
      
