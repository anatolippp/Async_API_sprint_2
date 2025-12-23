from celery import Celery

from ..core.config import settings


celery_app = Celery(
    "note",
    broker=f"amqp://guest:guest@{settings.rabbit_host}:{settings.rabbit_port}//",
    backend=f"redis://{settings.redis_host}:{settings.redis_port}/0",
)
celery_app.conf.task_default_queue = "notifications"
celery_app.conf.task_routes = {"tasks.send_notification": {"queue": "notifications"}}
celery_app.conf.broker_transport_options = {
    "queue_order_strategy": "priority",
    "max_retries": 3,
    "visibility_timeout": 1800,
}
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1
