import os

import celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
app = celery.Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
