from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product
from recommendation.logic.singleton import get_image_search_model 



'''
@receiver(post_save, sender=Size)
def delete_empty_size(sender, instance, **kwargs):
    if instance.quantity == 0:  
        instance.delete()  


@receiver(post_delete, sender=Size)
def delete_product_if_no_sizes_left(sender, instance, **kwargs):
    product = instance.product
    if not product.sizes.exists(): 
        product.delete() 
'''

'''
@receiver(post_save, sender=Product)
def product_created(sender, instance, created, **kwargs):
    if created:
        img_model = get_image_search_model()
        if img_model is not None:
            image_url = 'https://res.cloudinary.com/doz6xoqzu/'
            image_url += instance.image.public_id  
            img_model.addProduct(instance.id, image_url)

@receiver(post_delete, sender=Product)
def product_deleted(sender, instance, **kwargs):
    img_model = get_image_search_model()
    if img_model is not None:
        img_model.deleteProduct(instance.id)
'''