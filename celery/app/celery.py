from celery import Celery

celery_app = Celery('config')

celery_app.config_from_object('config', namespace='CELERY')

celery_app.autodiscover_tasks(['app'])
