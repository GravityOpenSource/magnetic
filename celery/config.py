# Celery相关配置
CELERY_RESULT_BACKEND = "redis://redis-server:6379/2"
CELERY_BROKER_URL = "redis://redis-server:6379/2"
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_WORKER_POOL_RESTARTS = True
CELERY_TASK_ACKS_LATE = True
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 60 * 60 * 24 * 365}
CELERY_WORKER_MAX_TASKS_PER_CHILD = 3
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ROUTES = {}