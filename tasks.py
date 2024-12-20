from celery_worker import celery

@celery.task
def process_task():
 pass