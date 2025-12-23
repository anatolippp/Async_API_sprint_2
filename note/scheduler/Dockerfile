FROM python:3.11-slim

WORKDIR /app
COPY scheduler/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY api/app ./app
COPY scheduler/scheduler.py ./scheduler.py
CMD ["python", "scheduler.py"]
