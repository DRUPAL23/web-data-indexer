from celery import Celery
import os

celery_app = Celery('web_data_indexer', broker=os.getenv('REDIS_URL','redis://localhost:6379/0'), backend=os.getenv('REDIS_URL','redis://localhost:6379/0'))
celery_app.conf.task_routes = {'workers.tasks.*': {'queue': 'crawler'}}
