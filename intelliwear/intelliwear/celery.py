import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelliwear.settings')

app = Celery('intelliwear')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

