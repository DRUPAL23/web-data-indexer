FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY workers ./workers
CMD ["celery","-A","workers.celery_app:celery_app","worker","--loglevel=INFO","--concurrency=4"]
