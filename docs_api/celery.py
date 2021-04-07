import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docs_api.settings')

app = Celery('docs_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'checkFtp':{
        'task':'api.tasks.checkFtp',
        'schedule' : crontab(minute='*/50')
    },
    'checkOstatok':{
            'task':'api.tasks.checkOstatok',
            'schedule' : crontab(minute='*/55')
        }
}