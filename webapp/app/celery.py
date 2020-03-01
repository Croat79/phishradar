import os

from celery import (
    Celery,
    shared_task,
)
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()