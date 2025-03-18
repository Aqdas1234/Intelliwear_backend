from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Size, Product


@receiver(post_save, sender=Size)
def delete_empty_size(sender, instance, **kwargs):
    if instance.quantity == 0:  
        instance.delete()  


@receiver(post_delete, sender=Size)
def delete_product_if_no_sizes_left(sender, instance, **kwargs):
    product = instance.product
    if not product.sizes.exists(): 
        product.delete() 
