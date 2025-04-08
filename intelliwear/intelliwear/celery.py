import os
from celery import Celery
from celery.schedules import crontab 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelliwear.settings')

app = Celery('intelliwear')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'train-cf-model-every-7-days': {
        'task': 'recommendation.tasks.train_cf_model_task',  
        'schedule': crontab(hour=0, minute=0, day_of_week='sunday'),  
    },
}

app.conf.timezone = 'UTC' 