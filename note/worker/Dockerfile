FROM python:3.11-slim

WORKDIR /app
COPY worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY api/app ./app
COPY worker/worker.py ./worker.py
CMD ["celery", "-A", "worker:celery_app", "worker", "--loglevel=info"]
