import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery = Celery("webdata_indexer", broker=redis_url, backend=redis_url)

# Basic routing to put crawler tasks on their own queue
celery.conf.task_routes = {"app.tasks.*": {"queue": "crawler"}}

# Optional: tuning values can be set here
