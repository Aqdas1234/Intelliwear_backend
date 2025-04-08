from celery import shared_task
from django.core.management import call_command
from recommendation.logic.singleton import get_cf_model,get_cb_model

@shared_task
def generate_similar_products_task():
    call_command('generate_similar_products')


@shared_task
def train_cf_model_task():
    cf_model = get_cf_model()
    if cf_model is not None:
        cf_model.train()  
    else:
        print("Error: CF model is None. Training cannot proceed.")

@shared_task
def train_cb_model_task():
    cb_model = get_cb_model()  
    if cb_model is not None:
        cb_model.train()  
    else:
        print("Error: CB model is None. Training cannot proceed.")
