from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from pydantic import Field
from pydantic_settings import BaseSettings

from app.services.queue import celery_app


class Settings(BaseSettings):
    interval: int = Field(3600, validation_alias="SCHEDULER_INTERVAL_SECONDS")

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
scheduler = BlockingScheduler()


@scheduler.scheduled_job("interval", seconds=settings.interval)
def generate_periodic_event():
    celery_app.send_task(
        "tasks.send_notification",
        kwargs={"notification_id": 0, "user_id": "*"},
        queue="notifications",
    )
    print(f"Scheduled periodic notification at {datetime.utcnow()}")


if __name__ == "__main__":
    scheduler.start()
