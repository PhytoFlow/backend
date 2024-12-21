
from celery import Celery

def make_celery():
    celery = Celery(
        'pythoflow',
        broker='CELERY_BROKER_URL',
        backend='CELERY_RESULT_BACKEND'
    )

    celery.conf.beat_schedule = {
        'run-every-5-minutes': {
            'task': 'app.my_periodic_task',
            'schedule': 300.0,  # 300 seconds = 5 minutes
        },
    }
    return celery  

my_app_celery = make_celery()